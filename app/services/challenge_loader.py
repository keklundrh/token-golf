"""
Token Golf - Challenge Loader Service

Loads challenge definitions from YAML files with three-tier caching:
1. In-memory cache (fastest)
2. Database (persistent)
3. YAML files (source of truth)

Supports both preload (startup) and lazy loading (on-demand).
See ADR 007 for design decisions.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge

logger = logging.getLogger(__name__)


class ChallengeLoaderService:
    """
    Service for loading and managing challenge definitions.

    Implements three-tier caching:
    - Tier 1: In-memory dictionary (fastest)
    - Tier 2: Database (persistent)
    - Tier 3: YAML files (source of truth)

    Usage:
        loader = ChallengeLoaderService(db_session, challenges_dir)

        # Preload all at startup
        await loader.preload_all_challenges()

        # Or load on-demand
        challenge = await loader.get_challenge("hole-001")
    """

    def __init__(self, db_session: AsyncSession, challenges_dir: Path | str):
        """
        Initialize the challenge loader.

        Args:
            db_session: SQLAlchemy async session for database access
            challenges_dir: Path to challenges directory (e.g., "./challenges")
        """
        self._db = db_session
        self._challenges_dir = Path(challenges_dir)
        self._cache: Dict[str, Challenge] = {}

        if not self._challenges_dir.exists():
            logger.warning(f"Challenges directory not found: {self._challenges_dir}")

    async def get_challenge(self, challenge_id: str) -> Challenge | None:
        """
        Get a challenge by ID using three-tier lookup.

        Lookup order:
        1. In-memory cache (fastest)
        2. Database (persistent)
        3. YAML file (source of truth)

        Args:
            challenge_id: Challenge identifier (e.g., "hole-001")

        Returns:
            Challenge object or None if not found

        Raises:
            ValueError: If challenge YAML is invalid
            FileNotFoundError: If challenge file doesn't exist
        """
        # Tier 1: In-memory cache
        if challenge_id in self._cache:
            logger.debug(f"Challenge {challenge_id} found in cache")
            return self._cache[challenge_id]

        # Tier 2: Database
        db_challenge = await self._get_from_database(challenge_id)
        if db_challenge:
            logger.debug(f"Challenge {challenge_id} found in database")
            self._cache[challenge_id] = db_challenge
            return db_challenge

        # Tier 3: YAML file
        logger.info(f"Loading challenge {challenge_id} from YAML")
        yaml_challenge = await self._load_from_yaml(challenge_id)
        if yaml_challenge:
            await self._save_to_database(yaml_challenge)
            self._cache[challenge_id] = yaml_challenge
            return yaml_challenge

        logger.warning(f"Challenge {challenge_id} not found")
        return None

    async def preload_all_challenges(self) -> int:
        """
        Load all challenges at startup.

        Scans challenges directory, loads all challenge.yaml files,
        validates them, and stores in database + cache.

        Returns:
            Number of challenges successfully loaded

        Raises:
            ValueError: If any challenge has invalid format
            FileNotFoundError: If challenges directory doesn't exist
        """
        if not self._challenges_dir.exists():
            raise FileNotFoundError(
                f"Challenges directory not found: {self._challenges_dir}"
            )

        # Find all challenge.yaml files
        challenge_files = list(self._challenges_dir.glob("*/challenge.yaml"))

        if not challenge_files:
            logger.warning(f"No challenge files found in {self._challenges_dir}")
            return 0

        logger.info(f"Preloading {len(challenge_files)} challenges...")

        loaded_count = 0
        errors = []

        for yaml_file in challenge_files:
            challenge_id = yaml_file.parent.name

            try:
                challenge = await self._load_from_yaml(challenge_id)
                if challenge:
                    await self._save_to_database(challenge)
                    self._cache[challenge_id] = challenge
                    loaded_count += 1
                    logger.debug(f"Loaded challenge: {challenge_id}")
            except Exception as e:
                error_msg = f"Failed to load {challenge_id}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        # Fail fast if any challenges are invalid
        if errors:
            error_summary = "\n".join(errors)
            raise ValueError(
                f"Failed to preload {len(errors)} challenge(s):\n{error_summary}"
            )

        logger.info(f"Successfully preloaded {loaded_count} challenges")
        return loaded_count

    async def list_challenges(
        self,
        difficulty: str | None = None,
        task_type: str | None = None,
    ) -> List[Challenge]:
        """
        List all challenges with optional filters.

        If cache is empty, loads from database.

        Args:
            difficulty: Filter by difficulty (easy, medium, hard, expert)
            task_type: Filter by task type (coding, extraction, etc.)

        Returns:
            List of Challenge objects matching filters
        """
        # If cache is empty, try loading from database
        if not self._cache:
            await self._load_all_from_database()

        # Filter cached challenges
        challenges = list(self._cache.values())

        if difficulty:
            challenges = [c for c in challenges if c.difficulty == difficulty]

        if task_type:
            challenges = [c for c in challenges if c.task_type == task_type]

        return challenges

    def clear_cache(self) -> None:
        """
        Clear in-memory cache.

        Useful for testing or forcing reload from database/YAML.
        """
        logger.info("Clearing challenge cache")
        self._cache.clear()

    # ========================================================================
    # Private Methods
    # ========================================================================

    async def _get_from_database(self, challenge_id: str) -> Challenge | None:
        """Load challenge from database."""
        stmt = select(Challenge).where(Challenge.id == challenge_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def _load_all_from_database(self) -> None:
        """Load all challenges from database into cache."""
        stmt = select(Challenge)
        result = await self._db.execute(stmt)
        challenges = result.scalars().all()

        for challenge in challenges:
            self._cache[challenge.id] = challenge

        logger.debug(f"Loaded {len(challenges)} challenges from database")

    async def _save_to_database(self, challenge: Challenge) -> None:
        """Save or update challenge in database."""
        # Check if challenge already exists
        existing = await self._get_from_database(challenge.id)

        if existing:
            # Update existing challenge
            existing.name = challenge.name
            existing.difficulty = challenge.difficulty
            existing.task_type = challenge.task_type
            existing.config_yaml = challenge.config_yaml
            logger.debug(f"Updated challenge in database: {challenge.id}")
        else:
            # Add new challenge
            self._db.add(challenge)
            logger.debug(f"Added challenge to database: {challenge.id}")

        await self._db.commit()

    async def _load_from_yaml(self, challenge_id: str) -> Challenge | None:
        """
        Load challenge from YAML file.

        Args:
            challenge_id: Challenge identifier (e.g., "hole-001")

        Returns:
            Challenge object or None if file not found

        Raises:
            ValueError: If YAML is invalid or missing required fields
        """
        yaml_file = self._challenges_dir / challenge_id / "challenge.yaml"

        if not yaml_file.exists():
            logger.warning(f"Challenge file not found: {yaml_file}")
            return None

        try:
            with open(yaml_file, "r") as f:
                config = yaml.safe_load(f)

            # Validate required fields
            self._validate_challenge_config(config, challenge_id)

            # Create Challenge model
            challenge = Challenge(
                id=config["id"],
                name=config["name"],
                difficulty=config.get("difficulty"),
                task_type=config.get("task_type"),
                config_yaml=yaml.dump(config),
                created_at=datetime.utcnow(),
            )

            return challenge

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {yaml_file}: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required field in {yaml_file}: {e}")

    def _validate_challenge_config(self, config: dict, challenge_id: str) -> None:
        """
        Validate challenge configuration has required fields.

        Args:
            config: Parsed YAML configuration
            challenge_id: Challenge identifier for error messages

        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = ["id", "name", "description", "task_type", "validation"]

        for field in required_fields:
            if field not in config:
                raise ValueError(
                    f"Challenge {challenge_id} missing required field: {field}"
                )

        # Validate ID matches directory name
        if config["id"] != challenge_id:
            raise ValueError(
                f"Challenge ID mismatch: directory={challenge_id}, "
                f"yaml id={config['id']}"
            )

        # Validate difficulty if present
        valid_difficulties = ["easy", "medium", "hard", "expert"]
        if "difficulty" in config and config["difficulty"] not in valid_difficulties:
            raise ValueError(
                f"Challenge {challenge_id} has invalid difficulty: "
                f"{config['difficulty']}. Must be one of {valid_difficulties}"
            )

        # Validate task_type
        valid_task_types = ["coding", "extraction", "question_answering", "generation"]
        if config["task_type"] not in valid_task_types:
            raise ValueError(
                f"Challenge {challenge_id} has invalid task_type: "
                f"{config['task_type']}. Must be one of {valid_task_types}"
            )

        # Validate validation section (required field)
        if "type" not in config["validation"]:
            raise ValueError(
                f"Challenge {challenge_id} missing validation.type field"
            )

        # Validate validation.type is valid
        valid_validation_types = ["test_cases", "exact_match", "pattern_match",
                                   "semantic_similarity", "custom_script", "multiple_choice"]
        if config["validation"]["type"] not in valid_validation_types:
            raise ValueError(
                f"Challenge {challenge_id} has invalid validation.type: "
                f"{config['validation']['type']}. Must be one of {valid_validation_types}"
            )

        # Validate validation.criteria exists (required for most validation types)
        validation_type = config["validation"]["type"]
        if validation_type in ["test_cases", "exact_match", "multiple_choice"]:
            if "criteria" not in config["validation"]:
                raise ValueError(
                    f"Challenge {challenge_id} with validation.type='{validation_type}' "
                    f"must have validation.criteria field"
                )

        # Validate optional fields if present
        self._validate_optional_fields(config, challenge_id)

        logger.debug(f"Challenge {challenge_id} passed validation")

    def _validate_optional_fields(self, config: dict, challenge_id: str) -> None:
        """
        Validate optional fields structure if present.

        Args:
            config: Parsed YAML configuration
            challenge_id: Challenge identifier for error messages

        Raises:
            ValueError: If optional fields have invalid structure
        """
        # Validate context_files if present
        if "context_files" in config:
            if not isinstance(config["context_files"], list):
                raise ValueError(
                    f"Challenge {challenge_id}: context_files must be a list"
                )
            for i, ctx_file in enumerate(config["context_files"]):
                if not isinstance(ctx_file, dict):
                    raise ValueError(
                        f"Challenge {challenge_id}: context_files[{i}] must be a dict"
                    )
                required_ctx_fields = ["name", "path"]
                for field in required_ctx_fields:
                    if field not in ctx_file:
                        raise ValueError(
                            f"Challenge {challenge_id}: context_files[{i}] "
                            f"missing required field: {field}"
                        )

        # Validate system_prompt if present
        if "system_prompt" in config:
            if not isinstance(config["system_prompt"], dict):
                raise ValueError(
                    f"Challenge {challenge_id}: system_prompt must be a dict"
                )
            if "default" not in config["system_prompt"]:
                raise ValueError(
                    f"Challenge {challenge_id}: system_prompt missing 'default' field"
                )

        # Validate parameters if present
        if "parameters" in config:
            if not isinstance(config["parameters"], dict):
                raise ValueError(
                    f"Challenge {challenge_id}: parameters must be a dict"
                )
            # Validate numeric parameters if present
            numeric_params = ["max_iterations", "time_limit_seconds", "hints_available"]
            for param in numeric_params:
                if param in config["parameters"]:
                    value = config["parameters"][param]
                    if value is not None and not isinstance(value, int):
                        raise ValueError(
                            f"Challenge {challenge_id}: parameters.{param} "
                            f"must be an integer or null, got {type(value).__name__}"
                        )
