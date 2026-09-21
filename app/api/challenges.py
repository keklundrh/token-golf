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
    total: int = Field(..., description="Total number of challenges")
    filtered: int = Field(..., description="Number after filtering")


# API Endpoints


@router.get(
    "",
    response_model=ChallengeListResponse,
    summary="List all challenges",
    description="Retrieve a list of all available challenges with optional filtering",
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
    db: AsyncSession = Depends(get_db),
) -> ChallengeListResponse:
    """
    List all challenges with optional filtering.

    Filters:
    - difficulty: easy, medium, hard, expert
    - task_type: coding, extraction, question_answering, generation

    Returns list of challenge metadata (id, name, difficulty, type, estimates).
    """
    try:
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

        logger.info(
            f"Listed {len(challenge_metadata)} challenges "
            f"(filtered from {len(all_challenges)} total)"
        )

        return ChallengeListResponse(
            challenges=challenge_metadata,
            total=len(all_challenges),
            filtered=len(challenge_metadata),
        )

    except Exception as e:
        logger.error(f"Error listing challenges: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list challenges: {str(e)}")


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
        challenge = await loader.get_challenge(challenge_id)

        if not challenge:
            raise HTTPException(
                status_code=404,
                detail=f"Challenge '{challenge_id}' not found",
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

        logger.info(f"Retrieved challenge: {challenge_id}")

        return detail

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving challenge {challenge_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve challenge: {str(e)}",
        )
