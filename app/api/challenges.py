"""
Token Golf - Challenge API Endpoints

REST API for challenge operations:
- List all challenges with filtering
- Retrieve specific challenge by ID
- Challenge metadata queries
"""

import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.services import ChallengeLoaderService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


# Pydantic Response Models
class ChallengeMetadata(BaseModel):
    """Challenge metadata for listing."""

    id: str = Field(..., description="Challenge unique identifier")
    name: str = Field(..., description="Challenge display name")
    difficulty: str = Field(..., description="Challenge difficulty level")
    task_type: str = Field(..., description="Type of challenge (coding, extraction, etc.)")
    estimated_tokens_expert: Optional[int] = Field(
        None, description="Estimated tokens for expert completion"
    )
    estimated_tokens_beginner: Optional[int] = Field(
        None, description="Estimated tokens for beginner completion"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "hole-001",
                "name": "Simple Function Generation",
                "difficulty": "easy",
                "task_type": "coding",
                "estimated_tokens_expert": 150,
                "estimated_tokens_beginner": 800,
            }
        }


class ValidationCriteria(BaseModel):
    """Validation configuration."""

    type: str = Field(..., description="Validation type (test_cases, exact_match, etc.)")
    # Additional fields will be dynamic based on validation type


class ChallengeDetail(BaseModel):
    """Complete challenge details."""

    id: str = Field(..., description="Challenge unique identifier")
    name: str = Field(..., description="Challenge display name")
    difficulty: str = Field(..., description="Challenge difficulty level")
    task_type: str = Field(..., description="Type of challenge")
    description: str = Field(..., description="Challenge description and instructions")
    validation_type: str = Field(..., description="How responses are validated")
    system_prompt_default: Optional[str] = Field(
        None, description="Default system prompt for this challenge"
    )
    system_prompt_removable: bool = Field(
        False, description="Whether system prompt can be removed"
    )
    system_prompt_editable: bool = Field(
        False, description="Whether system prompt can be edited"
    )
    context_files: Optional[List[dict]] = Field(
        None, description="Available context files for this challenge"
    )
    estimated_tokens_expert: Optional[int] = None
    estimated_tokens_beginner: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "hole-001",
                "name": "Add Two Numbers",
                "difficulty": "easy",
                "task_type": "coding",
                "description": "Write a Python function that adds two numbers.",
                "validation_type": "test_cases",
                "system_prompt_default": "You are a helpful coding assistant.",
                "system_prompt_removable": False,
                "system_prompt_editable": True,
                "context_files": [],
                "estimated_tokens_expert": 150,
                "estimated_tokens_beginner": 800,
            }
        }


class ChallengeListResponse(BaseModel):
    """Response for challenge listing."""

    challenges: List[ChallengeMetadata] = Field(..., description="List of challenges")
    total: int = Field(..., description="Total number of challenges (unfiltered)")
    filtered: int = Field(..., description="Number of challenges after filtering")
    page: int = Field(..., description="Current page number (1-based)")
    per_page: int = Field(..., description="Number of challenges per page")
    has_more: bool = Field(..., description="Whether there are more challenges to load")


# API Endpoints


@router.get(
    "",
    response_model=ChallengeListResponse,
    summary="List all challenges",
    description="Retrieve a list of all available challenges with optional filtering and pagination",
)
async def list_challenges(
    difficulty: Optional[str] = Query(
        None,
        description="Filter by difficulty (easy, medium, hard, expert)",
    ),
    task_type: Optional[str] = Query(
        None,
        description="Filter by task type (coding, extraction, question_answering, generation)",
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number (1-based)",
    ),
    per_page: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of challenges per page (max 100)",
    ),
    db: AsyncSession = Depends(get_db),
) -> ChallengeListResponse:
    """
    List all challenges with optional filtering and pagination.

    Filters:
    - difficulty: easy, medium, hard, expert
    - task_type: coding, extraction, question_answering, generation

    Returns paginated list of challenge metadata (id, name, difficulty, type, estimates).
    """
    try:
        # Validate difficulty filter
        valid_difficulties = ["easy", "medium", "hard", "expert"]
        if difficulty and difficulty not in valid_difficulties:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_difficulty",
                    "message": f"Invalid difficulty '{difficulty}'.",
                    "details": {
                        "field": "difficulty",
                        "value": difficulty,
                        "valid_values": valid_difficulties,
                    },
                    "suggestions": [
                        f"Use one of: {', '.join(valid_difficulties)}",
                    ],
                },
            )

        # Validate task_type filter
        valid_task_types = ["coding", "extraction", "question_answering", "generation"]
        if task_type and task_type not in valid_task_types:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_task_type",
                    "message": f"Invalid task_type '{task_type}'.",
                    "details": {
                        "field": "task_type",
                        "value": task_type,
                        "valid_values": valid_task_types,
                    },
                    "suggestions": [
                        f"Use one of: {', '.join(valid_task_types)}",
                    ],
                },
            )

        # Get challenge loader service
        challenges_dir = Path(settings.challenges_dir)
        loader = ChallengeLoaderService(db, challenges_dir)

        # List challenges with filters
        challenges = await loader.list_challenges(
            difficulty=difficulty,
            task_type=task_type,
        )

        # Convert to metadata models
        challenge_metadata = []
        for challenge in challenges:
            # Parse config to extract metadata
            import yaml

            config = yaml.safe_load(challenge.config_yaml)

            metadata = ChallengeMetadata(
                id=challenge.id,
                name=config.get("name", "Unnamed Challenge"),
                difficulty=config.get("difficulty", "unknown"),
                task_type=config.get("task_type", "unknown"),
                estimated_tokens_expert=config.get("metadata", {}).get(
                    "estimated_tokens_expert"
                ),
                estimated_tokens_beginner=config.get("metadata", {}).get(
                    "estimated_tokens_beginner"
                ),
            )
            challenge_metadata.append(metadata)

        # Get total count (unfiltered)
        all_challenges = await loader.list_challenges()
        total_count = len(all_challenges)
        filtered_count = len(challenge_metadata)

        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_challenges = challenge_metadata[start_idx:end_idx]
        has_more = end_idx < filtered_count

        logger.debug(
            f"Listed {len(paginated_challenges)} challenges on page {page} "
            f"(filtered: {filtered_count}, total: {total_count})"
        )

        return ChallengeListResponse(
            challenges=paginated_challenges,
            total=total_count,
            filtered=filtered_count,
            page=page,
            per_page=per_page,
            has_more=has_more,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing challenges: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to list challenges.",
                "details": {"exception": str(e)},
                "suggestions": [
                    "Try again in a moment",
                    "Contact support if the problem persists",
                ],
            },
        )


@router.get(
    "/{challenge_id}",
    response_model=ChallengeDetail,
    summary="Get challenge details",
    description="Retrieve complete details for a specific challenge",
)
async def get_challenge(
    challenge_id: str,
    db: AsyncSession = Depends(get_db),
) -> ChallengeDetail:
    """
    Get complete details for a specific challenge.

    Args:
        challenge_id: Challenge identifier (e.g., "hole-001")

    Returns:
        Complete challenge configuration including:
        - Basic info (id, name, difficulty, type)
        - Description and instructions
        - Validation configuration
        - System prompt settings
        - Available context files
        - Token estimates
    """
    try:
        # Get challenge loader service
        challenges_dir = Path(settings.challenges_dir)
        loader = ChallengeLoaderService(db, challenges_dir)

        # Get challenge
        try:
            challenge = await loader.get_challenge(challenge_id)
        except ValueError:
            # Challenge not found
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "challenge_not_found",
                    "message": f"Challenge '{challenge_id}' not found.",
                    "details": {"challenge_id": challenge_id},
                    "suggestions": [
                        "Check that the challenge ID is correct",
                        "Use GET /api/challenges to see all available challenges",
                    ],
                },
            )

        if not challenge:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "challenge_not_found",
                    "message": f"Challenge '{challenge_id}' not found.",
                    "details": {"challenge_id": challenge_id},
                    "suggestions": [
                        "Check that the challenge ID is correct",
                        "Use GET /api/challenges to see all available challenges",
                    ],
                },
            )

        # Parse config
        import yaml

        config = yaml.safe_load(challenge.config_yaml)

        # Extract validation type
        validation_config = config.get("validation", {})
        validation_type = validation_config.get("type", "unknown")

        # Extract system prompt settings
        system_prompt_config = config.get("system_prompt", {})
        if isinstance(system_prompt_config, str):
            # Simple string format
            system_prompt_default = system_prompt_config
            system_prompt_removable = False
            system_prompt_editable = False
        else:
            # Object format
            system_prompt_default = system_prompt_config.get("default")
            system_prompt_removable = system_prompt_config.get("removable", False)
            system_prompt_editable = system_prompt_config.get("editable", False)

        # Extract context files
        context_files = config.get("context_files", [])

        # Build response
        detail = ChallengeDetail(
            id=challenge.id,
            name=config.get("name", "Unnamed Challenge"),
            difficulty=config.get("difficulty", "unknown"),
            task_type=config.get("task_type", "unknown"),
            description=config.get("description", ""),
            validation_type=validation_type,
            system_prompt_default=system_prompt_default,
            system_prompt_removable=system_prompt_removable,
            system_prompt_editable=system_prompt_editable,
            context_files=context_files,
            estimated_tokens_expert=config.get("metadata", {}).get(
                "estimated_tokens_expert"
            ),
            estimated_tokens_beginner=config.get("metadata", {}).get(
                "estimated_tokens_beginner"
            ),
        )

        logger.debug(f"Retrieved challenge: {challenge_id}")

        return detail

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving challenge {challenge_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Failed to retrieve challenge.",
                "details": {"challenge_id": challenge_id, "exception": str(e)},
                "suggestions": [
                    "Try again in a moment",
                    "Contact support if the problem persists",
                ],
            },
        )
