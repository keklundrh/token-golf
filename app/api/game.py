"""
Token Golf - Game API Endpoints

Orchestrates the game flow:
- Start new game session (with sign-in or new user creation)
- Submit prompt attempts
- Get game state
"""

from passlib.hash import bcrypt
import logging
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import Attempt, Challenge, Score, Session, SessionParticipant, User
from app.services import (
    ChallengeLoaderService,
    CourseLoaderService,
    LLMClient,
    ScoringService,
    SessionManager,
    ValidatorService,
)

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/game", tags=["game"])


# ============================================================================
# Pydantic Models
# ============================================================================


class ErrorDetail(BaseModel):
    """Structured error detail for validation errors."""

    field: str = Field(..., description="Field that caused the error")
    issue: str = Field(..., description="Description of the issue")


class ErrorResponse(BaseModel):
    """Consistent error response format."""

    error: str = Field(..., description="Short error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    suggestions: Optional[List[str]] = Field(
        None, description="Suggestions for fixing the error"
    )


class StartGameRequest(BaseModel):
    """Request to start a new game session."""

    # Authentication options (one must be provided)
    action: str = Field(
        ..., description="Action type: 'generate' or 'signin'"
    )
    username: Optional[str] = Field(
        None, description="Existing username (for sign-in, required if action='signin')"
    )
    password: Optional[str] = Field(
        None, description="Password (for sign-in, required if action='signin')"
    )
    course_id: Optional[str] = Field(
        "beginner-course", description="Course identifier (default: beginner-course)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "action": "generate",
                "course_id": "beginner-course",
            }
        }


class StartGameResponse(BaseModel):
    """Response after starting a game session."""

    session_id: str = Field(..., description="Unique session identifier")
    user_id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    password: Optional[str] = Field(
        None, description="Generated password (only if new user)"
    )
    course_id: str = Field(..., description="Course identifier")
    challenges: List[str] = Field(..., description="List of challenge IDs in order")
    current_challenge_id: Optional[str] = Field(
        None, description="Current challenge to attempt"
    )
    message: str = Field(..., description="Welcome message")
    next_action: str = Field(
        ..., description="Hint for frontend on what to do next"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-abc123",
                "user_id": 42,
                "username": "Blue-Pebblebeach-7",
                "password": "X7mK9nP2qR5t",
                "course_id": "beginner-course",
                "challenges": ["hole-001", "hole-002"],
                "current_challenge_id": "hole-001",
                "message": "Welcome Blue-Pebblebeach-7! Your course has 2 holes.",
                "next_action": "load_challenge",
            }
        }


class SubmitAttemptRequest(BaseModel):
    """Request to submit a prompt attempt."""

    session_id: str = Field(..., description="Session identifier")
    challenge_id: str = Field(..., description="Challenge identifier")
    user_prompt: str = Field(..., description="User's prompt")
    action: str = Field(
        "practice",
        description="Action type: 'practice' (practice swing, not recorded) or 'submit' (record score)"
    )
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    context_files: Optional[List[dict]] = Field(
        None, description="Context files to include"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-abc123",
                "challenge_id": "hole-001",
                "user_prompt": "Write a function to add two numbers",
                "action": "practice",
                "system_prompt": "You are a helpful coding assistant.",
                "context_files": [],
            }
        }


class SubmitAttemptResponse(BaseModel):
    """Response after submitting an attempt."""

    attempt_id: int = Field(..., description="Attempt identifier")
    attempt_type: str = Field(..., description="Type: 'practice' or 'submitted'")
    is_correct: bool = Field(..., description="Whether the answer was correct")
    validation_message: str = Field(..., description="Validation feedback")
    input_tokens: int = Field(..., description="Input tokens used")
    output_tokens: int = Field(..., description="Output tokens used")
    total_tokens: int = Field(..., description="Total tokens for this attempt")
    cumulative_tokens: int = Field(
        ..., description="Cumulative tokens from submitted attempts only"
    )
    attempt_number: int = Field(..., description="Attempt number for this challenge")
    practice_count: int = Field(..., description="Number of practice swings taken")
    submitted_count: int = Field(..., description="Number of submitted attempts")
    llm_response: str = Field(..., description="LLM's response")
    next_action: str = Field(
        ..., description="Hint for frontend on what to do next"
    )
    suggestions: Optional[List[str]] = Field(
        None, description="Helpful suggestions if attempt was incorrect"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": 123,
                "is_correct": True,
                "validation_message": "All test cases passed!",
                "input_tokens": 150,
                "output_tokens": 75,
                "total_tokens": 225,
                "cumulative_tokens": 450,
                "attempt_number": 2,
                "llm_response": "def add(a, b):\n    return a + b",
                "next_action": "next_challenge",
                "suggestions": None,
            }
        }


class GameStatusResponse(BaseModel):
    """Response with current game state."""

    session_id: str
    user_id: int
    username: str
    course_id: str
    session_status: str
    challenges: List[dict]
    current_challenge_id: Optional[str]
    total_tokens: int
    completed_challenges: int
    rank: str = "-"

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-abc123",
                "user_id": 42,
                "username": "Blue-Pebblebeach-7",
                "course_id": "beginner-course",
                "session_status": "active",
                "challenges": [
                    {
                        "id": "hole-001",
                        "name": "Add Two Numbers",
                        "completed": True,
                        "attempts": 2,
                        "tokens": 450,
                    }
                ],
                "current_challenge_id": "hole-002",
                "total_tokens": 450,
                "completed_challenges": 1,
            }
        }


# ============================================================================
# Helper Functions
# ============================================================================


def generate_username() -> str:
    """Generate a username in Color-Course-Club format."""
    colors = [
        "Red",
        "Blue",
        "Green",
        "Yellow",
        "Orange",
        "Purple",
        "Pink",
        "Teal",
        "Gold",
        "Silver",
    ]
    courses = [
        "Augusta",
        "Pebblebeach",
        "StAndrews",
        "Pinehurst",
        "Oakmont",
        "Shinnecock",
        "Merion",
        "Cypress",
    ]
    clubs = list(range(1, 15))  # Golf clubs 1-14

    color = secrets.choice(colors)
    course = secrets.choice(courses)
    club = secrets.choice(clubs)

    return f"{color}-{course}-{club}"


def generate_password(length: int = 12) -> str:
    """Generate a random password."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password (truncated to 72 bytes if longer)

    Returns:
        Bcrypt hashed password string
    """
    # Bcrypt has a max password length of 72 bytes
    # Truncate password bytes to 72, handling UTF-8 properly
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        password_bytes = password_bytes[:72]
        # Decode back, ignoring any incomplete multi-byte sequences at the end
        password = password_bytes.decode('utf-8', errors='ignore')

    return bcrypt.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.verify(plain_password, hashed_password)


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/start", response_model=StartGameResponse, status_code=status.HTTP_201_CREATED)
async def start_game(
    request: StartGameRequest,
    db: AsyncSession = Depends(get_db),
) -> StartGameResponse:
    """
    Start a new game session.

    Two options:
    1. Generate new user: action="generate"
    2. Sign in with existing credentials: action="signin" (requires username + password)
    """
    logger.debug(f"Starting new game session: action={request.action}, course_id={request.course_id}")

    # Validate action field
    if request.action not in ["generate", "signin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_action",
                "message": f"Invalid action '{request.action}'. Must be 'generate' or 'signin'.",
                "details": {"field": "action", "value": request.action},
                "suggestions": [
                    "Use action='generate' to create a new user",
                    "Use action='signin' with username and password to sign in",
                ],
            },
        )

    # Validate course_id using courses.yaml
    challenges_dir = Path(settings.challenges_dir)
    course_loader = CourseLoaderService(challenges_dir)

    if not course_loader.validate_course_id(request.course_id):
        valid_courses = course_loader.list_course_ids()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_course",
                "message": f"Course '{request.course_id}' not found.",
                "details": {"field": "course_id", "valid_courses": valid_courses},
                "suggestions": [
                    f"Use one of the available courses: {', '.join(valid_courses)}",
                ],
            },
        )

    user = None
    generated_password = None

    # Option 1: Sign in with existing credentials
    if request.action == "signin":
        # Validate required fields
        if not request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "missing_username",
                    "message": "Username is required for sign-in.",
                    "details": {"field": "username"},
                    "suggestions": [
                        "Provide your username in the request",
                        "Or use action='generate' to create a new user",
                    ],
                },
            )

        if not request.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "missing_password",
                    "message": "Password is required for sign-in.",
                    "details": {"field": "password"},
                    "suggestions": [
                        "Provide your password in the request",
                    ],
                },
            )

        logger.debug(f"Attempting sign-in for username: {request.username}")

        # Find user by username
        result = await db.execute(select(User).where(User.username == request.username))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "user_not_found",
                    "message": f"User '{request.username}' not found.",
                    "details": {"username": request.username},
                    "suggestions": [
                        "Check that you spelled your username correctly",
                        "Use action='generate' to create a new account",
                    ],
                },
            )

        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_password",
                    "message": "Invalid password.",
                    "details": {},
                    "suggestions": [
                        "Check that you entered the correct password",
                        "Passwords are case-sensitive",
                    ],
                },
            )

        logger.debug(f"Sign-in successful for user {user.id}: {user.username}")

    # Option 2: Generate new user
    elif request.action == "generate":
        logger.debug("Generating new user")

        # Generate unique username
        max_attempts = 10
        for _ in range(max_attempts):
            username = generate_username()
            # Check if username exists
            result = await db.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                break
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "username_generation_failed",
                    "message": "Failed to generate unique username after multiple attempts.",
                    "details": {},
                    "suggestions": [
                        "Try again in a moment",
                    ],
                },
            )

        # Generate password
        generated_password = generate_password()

        # Create user
        user = User(
            username=username,
            password_hash=hash_password(generated_password),
            created_at=datetime.utcnow(),
        )
        db.add(user)
        await db.flush()  # Get user.id

        logger.debug(f"Created new user {user.id}: {user.username}")

    # Create session with requested course
    course_id = request.course_id

    # Get challenges for this specific course
    challenge_ids = course_loader.get_course_challenges(course_id)

    if not challenge_ids:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "no_challenges",
                "message": f"No challenges found for course '{course_id}'.",
                "details": {"course_id": course_id},
                "suggestions": [
                    "Contact support if this problem persists",
                ],
            },
        )

    # Create session
    session = Session(
        id=f"session-{secrets.token_urlsafe(8)}",
        course_id=course_id,
        created_at=datetime.utcnow(),
        timeout_hours=settings.session_timeout_hours,
        expires_at=datetime.utcnow()
        + timedelta(hours=settings.session_timeout_hours),
        status="active",
        course_total_holes=len(challenge_ids),  # Critical fix: set total holes for completion tracking
    )
    db.add(session)

    # Add user to session
    participant = SessionParticipant(
        session_id=session.id,
        user_id=user.id,
        joined_at=datetime.utcnow(),
    )
    db.add(participant)

    await db.commit()

    logger.debug(
        f"Created session {session.id} for user {user.id} with {len(challenge_ids)} challenges"
    )

    return StartGameResponse(
        session_id=session.id,
        user_id=user.id,
        username=user.username,
        password=generated_password,  # Only returned for new users
        course_id=course_id,
        challenges=challenge_ids,
        current_challenge_id=challenge_ids[0] if challenge_ids else None,
        message=f"Welcome {user.username}! Your course has {len(challenge_ids)} holes.",
        next_action="load_challenge",
    )


@router.post("/submit", response_model=SubmitAttemptResponse)
async def submit_attempt(
    request: SubmitAttemptRequest,
    db: AsyncSession = Depends(get_db),
) -> SubmitAttemptResponse:
    """
    Submit a prompt attempt for a challenge.

    Orchestrates: LLM Client → Validator → Scoring
    """
    logger.debug(
        f"Submitting attempt for session {request.session_id}, challenge {request.challenge_id}"
    )

    # Validate prompt is not empty
    if not request.user_prompt or not request.user_prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "empty_prompt",
                "message": "User prompt cannot be empty.",
                "details": {"field": "user_prompt"},
                "suggestions": [
                    "Provide a prompt for the LLM to generate a response",
                    "The prompt should describe what you want the LLM to do",
                ],
            },
        )

    # Validate action parameter (ADR 011: Practice Swings)
    if request.action not in ("practice", "submit"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "invalid_action",
                "message": f"Invalid action: {request.action}. Must be 'practice' or 'submit'.",
                "details": {"field": "action", "value": request.action},
                "suggestions": [
                    "Use 'practice' for practice swings (don't count toward score)",
                    "Use 'submit' to record your score (only successful attempts can be submitted)",
                ],
            },
        )

    # Verify session exists and is active (checks timeout automatically)
    session_manager = SessionManager(db)
    try:
        session = await session_manager.get_active_session(request.session_id)
    except HTTPException as e:
        # Re-raise with better error details
        if e.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "session_not_found",
                    "message": f"Session '{request.session_id}' not found.",
                    "details": {"session_id": request.session_id},
                    "suggestions": [
                        "Check that you have a valid session ID",
                        "Start a new game session with POST /api/game/start",
                    ],
                },
            )
        elif e.status_code == status.HTTP_400_BAD_REQUEST:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "session_not_active",
                    "message": "Session is not active or has expired.",
                    "details": {"session_id": request.session_id},
                    "suggestions": [
                        "Start a new game session with POST /api/game/start",
                    ],
                },
            )
        else:
            raise

    # Get user from session
    result = await db.execute(
        select(SessionParticipant)
        .where(SessionParticipant.session_id == request.session_id)
        .limit(1)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "no_participant",
                "message": "No participant found for this session.",
                "details": {"session_id": request.session_id},
                "suggestions": [
                    "This session may be invalid or corrupted",
                    "Start a new game session with POST /api/game/start",
                ],
            },
        )

    user_id = participant.user_id

    # Load challenge
    challenges_dir = Path(settings.challenges_dir)
    loader = ChallengeLoaderService(db, challenges_dir)

    try:
        challenge = await loader.get_challenge(request.challenge_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "challenge_not_found",
                "message": f"Challenge '{request.challenge_id}' not found.",
                "details": {"challenge_id": request.challenge_id},
                "suggestions": [
                    "Check that the challenge ID is correct",
                    "Use GET /api/challenges to see available challenges",
                ],
            },
        )

    # Step 1: Call LLM
    llm_client = LLMClient(api_key=settings.claude_api_key)

    # Include active context file contents in the prompt (pills affect tokens)
    ctx_contents = []
    for cf in request.context_files or []:
        content = cf.get("content") if isinstance(cf, dict) else None
        if content:
            ctx_contents.append(str(content))

    try:
        llm_response = await llm_client.complete_with_context(
            prompt=request.user_prompt,
            context_files=ctx_contents,
            system_prompt=request.system_prompt,
        )
    except (ConnectionError, TimeoutError, RuntimeError) as e:
        # Only catch LLM-related errors for weather delay
        # ConnectionError: Network issues
        # TimeoutError: LLM timeout
        # RuntimeError: LLM service errors
        logger.error(f"LLM API error (weather delay): {e}")

        # Weather delay: clear this hole's tokens unless already completed
        # (CLAUDE.md: "Completed holes remain untouched").
        scoring_service = ScoringService(db)
        existing = await scoring_service.get_score(
            user_id=user_id,
            session_id=request.session_id,
            challenge_id=request.challenge_id,
        )
        if existing is None or existing.completed_at is None:
            await scoring_service.clear_challenge_score(
                user_id=user_id,
                session_id=request.session_id,
                challenge_id=request.challenge_id,
            )
            await db.commit()
            detail = {
                "error": "weather_delay",
                "message": "LLM service temporarily unavailable. Your tokens for this hole have been cleared.",
                "details": {"challenge_id": request.challenge_id},
                "suggestions": [
                    "Try again in a few moments",
                    "The LLM service may be experiencing high load",
                ],
            }
        else:
            detail = {
                "error": "weather_delay",
                "message": "LLM service temporarily unavailable. Your completed score for this hole is preserved.",
                "details": {"challenge_id": request.challenge_id},
                "suggestions": [
                    "Try again in a few moments",
                    "Your completed score is safe",
                ],
            }

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )

    # Step 2: Validate response
    validator = ValidatorService()
    validation_result = await validator.validate(
        response=llm_response.response_text,
        challenge=challenge,
    )

    # Step 2.5: Block submission of failed attempts (ADR 011)
    if request.action == "submit" and not validation_result.is_correct:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "cannot_submit_incorrect",
                "message": "Cannot submit incorrect attempt. Only successful attempts can be recorded.",
                "details": {
                    "validation_message": validation_result.feedback or "Validation failed"
                },
                "suggestions": [
                    "Use 'practice' action to test your solution",
                    "Fix the validation errors and try again",
                    "Only submit when your solution passes all checks",
                ],
            },
        )

    # Step 3: Record attempt and score
    scoring_service = ScoringService(db)

    # Determine attempt_type based on action
    attempt_type = "submitted" if request.action == "submit" else "practice"

    attempt = await scoring_service.record_attempt(
        user_id=user_id,
        session_id=request.session_id,
        challenge_id=request.challenge_id,
        prompt=request.user_prompt,
        system_prompt=request.system_prompt,
        context_files=request.context_files or [],
        response=llm_response.response_text,
        input_tokens=llm_response.input_tokens,
        output_tokens=llm_response.output_tokens,
        is_correct=validation_result.is_correct,
        attempt_type=attempt_type,
    )

    await db.commit()

    # Get cumulative score (only from submitted attempts, per ADR 011)
    result = await db.execute(
        select(Score).where(
            Score.user_id == user_id,
            Score.session_id == request.session_id,
            Score.challenge_id == request.challenge_id,
        )
    )
    score = result.scalar_one_or_none()

    # Cumulative tokens = best submitted attempt (stored in Score table)
    # If no submitted attempts yet, show 0
    cumulative_tokens = score.total_tokens if score else 0

    # Calculate practice and submitted attempt counts
    practice_count = await scoring_service.count_attempts(
        user_id=user_id,
        challenge_id=request.challenge_id,
        attempt_type="practice",
    )
    submitted_count = await scoring_service.count_attempts(
        user_id=user_id,
        challenge_id=request.challenge_id,
        attempt_type="submitted",
    )

    logger.debug(
        f"{attempt_type.capitalize()} attempt {attempt.id} recorded: "
        f"is_correct={validation_result.is_correct}, "
        f"tokens={attempt.total_tokens}, cumulative={cumulative_tokens}, "
        f"practice={practice_count}, submitted={submitted_count}"
    )

    # Determine next action and suggestions (ADR 011 logic)
    if attempt_type == "practice" and validation_result.is_correct:
        next_action = "can_submit"
        suggestions = None
    elif attempt_type == "practice" and not validation_result.is_correct:
        next_action = "retry"
        suggestions = [
            "Review the validation feedback",
            "Try a more specific or different prompt",
            "Check the challenge requirements",
        ]
    elif attempt_type == "submitted":
        # Submitted attempts are always correct (blocked earlier if not)
        next_action = "next_challenge"
        suggestions = None
    else:
        # Fallback (shouldn't reach here)
        next_action = "retry"
        suggestions = None

    return SubmitAttemptResponse(
        attempt_id=attempt.id,
        attempt_type=attempt_type,
        is_correct=validation_result.is_correct,
        validation_message=validation_result.feedback or "",
        input_tokens=llm_response.input_tokens,
        output_tokens=llm_response.output_tokens,
        total_tokens=attempt.total_tokens,
        cumulative_tokens=cumulative_tokens,
        attempt_number=attempt.attempt_number,
        practice_count=practice_count,
        submitted_count=submitted_count,
        llm_response=llm_response.response_text,
        next_action=next_action,
        suggestions=suggestions,
    )


@router.get("/status/{session_id}", response_model=GameStatusResponse)
async def get_game_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> GameStatusResponse:
    """Get current game state for a session."""
    logger.debug(f"Getting game status for session {session_id}")

    # Get session (checks timeout and updates status if expired)
    session_manager = SessionManager(db)
    try:
        session = await session_manager.get_active_session(session_id)
    except HTTPException:
        # Session expired or inactive - still show status but with updated state
        # Re-fetch to get current status after timeout check
        result = await db.execute(select(Session).where(Session.id == session_id))
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found",
            )

    # Get participant (user)
    result = await db.execute(
        select(SessionParticipant)
        .where(SessionParticipant.session_id == session_id)
        .limit(1)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No participant found for session",
        )

    # Get user
    result = await db.execute(select(User).where(User.id == participant.user_id))
    user = result.scalar_one_or_none()

    # Get all scores for this session
    result = await db.execute(
        select(Score).where(
            Score.user_id == participant.user_id,
            Score.session_id == session_id,
        )
    )
    scores = result.scalars().all()

    # Get challenges for this session's course (not all challenges)
    challenges_dir = Path(settings.challenges_dir)
    course_loader = CourseLoaderService(challenges_dir)
    challenge_ids = course_loader.get_course_challenges(session.course_id)

    # Load challenge details for names
    loader = ChallengeLoaderService(db, challenges_dir)
    all_challenges = await loader.list_challenges()
    challenge_names = {c.id: (c.name or c.id) for c in all_challenges}

    # Build challenge status
    challenge_status = []
    total_tokens = 0
    completed_count = 0

    for chal_id in challenge_ids:
        score = next((s for s in scores if s.challenge_id == chal_id), None)
        if score:
            challenge_status.append({
                "id": chal_id,
                "name": challenge_names.get(chal_id, chal_id),
                "completed": score.completed_at is not None,
                "attempts": score.total_attempts,
                "tokens": score.total_tokens,
            })
            total_tokens += score.total_tokens
            if score.completed_at:
                completed_count += 1
        else:
            challenge_status.append({
                "id": chal_id,
                "name": chal_id,
                "completed": False,
                "attempts": 0,
                "tokens": 0,
            })

    # Calculate rank: compare against players with same number of completed holes
    rank = '-'
    if completed_count > 0:
        # Get all users' scores for this course
        result = await db.execute(
            select(Score)
            .join(SessionParticipant, Score.user_id == SessionParticipant.user_id)
            .join(Session, SessionParticipant.session_id == Session.id)
            .where(Session.course_id == session.course_id)
        )
        all_course_scores = result.scalars().all()

        # Group by user and calculate their stats
        from collections import defaultdict
        user_progress = defaultdict(lambda: {'completed': 0, 'total_tokens': 0})

        for score in all_course_scores:
            if score.completed_at:
                user_progress[score.user_id]['completed'] += 1
                user_progress[score.user_id]['total_tokens'] += score.total_tokens

        # Filter to users with same progress level
        same_progress_users = [
            (uid, data['total_tokens'])
            for uid, data in user_progress.items()
            if data['completed'] == completed_count
        ]

        # Sort by tokens (ascending - lower is better)
        same_progress_users.sort(key=lambda x: x[1])

        # Find current user's rank
        for idx, (uid, tokens) in enumerate(same_progress_users, start=1):
            if uid == user.id:
                rank = f"{idx}/{len(same_progress_users)}"
                break

    # Determine current challenge (first incomplete)
    current_challenge_id = None
    for chal in challenge_status:
        if not chal["completed"]:
            current_challenge_id = chal["id"]
            break

    return GameStatusResponse(
        session_id=session.id,
        user_id=user.id,
        username=user.username,
        course_id=session.course_id,
        session_status=session.status,
        challenges=challenge_status,
        current_challenge_id=current_challenge_id,
        total_tokens=total_tokens,
        completed_challenges=completed_count,
        rank=rank,
    )
