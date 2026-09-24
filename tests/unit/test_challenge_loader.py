"""
Unit tests for ChallengeLoaderService

Tests challenge loading from YAML, three-tier caching, course loading,
and validation logic.
"""

import pytest
import yaml
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

from app.services.challenge_loader import ChallengeLoaderService
from app.models.challenge import Challenge


class TestChallengeLoaderInit:
    """Test ChallengeLoaderService initialization."""

    @pytest.mark.asyncio
    async def test_init_with_valid_path(self, db_session, test_settings):
        """Test initialization with valid challenges directory."""
        loader = ChallengeLoaderService(db_session, test_settings.challenges_dir)

        assert loader._db == db_session
        assert loader._challenges_dir == Path(test_settings.challenges_dir)
        assert loader._cache == {}
        assert loader._courses_cache == {}

    @pytest.mark.asyncio
    async def test_init_with_nonexistent_path(self, db_session):
        """Test initialization with nonexistent directory logs warning."""
        with patch('app.services.challenge_loader.logger') as mock_logger:
            loader = ChallengeLoaderService(db_session, "/nonexistent/path")
            mock_logger.warning.assert_called_once()


class TestGetChallenge:
    """Test challenge retrieval with three-tier caching."""

    @pytest.mark.asyncio
    async def test_get_from_cache(self, db_session, challenge_loader):
        """Test retrieval from in-memory cache (Tier 1)."""
        # Pre-populate cache
        cached_challenge = Challenge(
            id="test-001",
            name="Test Challenge",
            difficulty="easy",
            task_type="coding",
            config_yaml="id: test-001\nname: Test",
            created_at=datetime.utcnow()
        )
        challenge_loader._cache["test-001"] = cached_challenge

        result = await challenge_loader.get_challenge("test-001")

        assert result == cached_challenge
        assert result.id == "test-001"

    @pytest.mark.asyncio
    async def test_get_from_database(self, db_session, challenge_loader):
        """Test retrieval from database (Tier 2)."""
        # Add challenge to database
        db_challenge = Challenge(
            id="test-002",
            name="DB Test",
            difficulty="medium",
            task_type="coding",
            config_yaml="id: test-002\nname: DB Test",
            created_at=datetime.utcnow()
        )
        db_session.add(db_challenge)
        await db_session.commit()

        result = await challenge_loader.get_challenge("test-002")

        assert result.id == "test-002"
        assert result.name == "DB Test"
        # Should also be cached now
        assert "test-002" in challenge_loader._cache

    @pytest.mark.asyncio
    async def test_get_nonexistent_challenge(self, db_session, challenge_loader):
        """Test retrieval of nonexistent challenge returns None."""
        result = await challenge_loader.get_challenge("nonexistent-999")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_population_from_database(self, db_session, challenge_loader):
        """Test that database results populate the cache."""
        db_challenge = Challenge(
            id="cache-test",
            name="Cache Test",
            difficulty="easy",
            task_type="coding",
            config_yaml="id: cache-test",
            created_at=datetime.utcnow()
        )
        db_session.add(db_challenge)
        await db_session.commit()

        # First call should hit database
        result1 = await challenge_loader.get_challenge("cache-test")
        assert "cache-test" in challenge_loader._cache

        # Second call should hit cache (test by clearing db)
        await db_session.delete(db_challenge)
        await db_session.commit()

        result2 = await challenge_loader.get_challenge("cache-test")
        assert result2 is not None
        assert result2.id == "cache-test"


class TestPreloadChallenges:
    """Test preloading all challenges at startup."""

    @pytest.mark.asyncio
    async def test_preload_success(self, db_session, challenge_loader):
        """Test successful preload of all challenges."""
        # This will load actual challenges from the challenges directory
        if Path(challenge_loader._challenges_dir).exists():
            count = await challenge_loader.preload_all_challenges()
            assert count > 0
            assert len(challenge_loader._cache) == count

    @pytest.mark.asyncio
    async def test_preload_nonexistent_dir(self, db_session):
        """Test preload with nonexistent directory raises error."""
        loader = ChallengeLoaderService(db_session, "/nonexistent/path")

        with pytest.raises(FileNotFoundError, match="Challenges directory not found"):
            await loader.preload_all_challenges()

    @pytest.mark.asyncio
    async def test_preload_empty_dir(self, db_session, tmp_path):
        """Test preload with empty directory returns 0."""
        empty_dir = tmp_path / "empty_challenges"
        empty_dir.mkdir()

        loader = ChallengeLoaderService(db_session, str(empty_dir))
        count = await loader.preload_all_challenges()

        assert count == 0

    @pytest.mark.asyncio
    async def test_preload_invalid_yaml_fails(self, db_session, tmp_path):
        """Test preload with invalid YAML raises error."""
        challenges_dir = tmp_path / "challenges"
        challenges_dir.mkdir()

        # Create invalid challenge
        invalid_dir = challenges_dir / "invalid-001"
        invalid_dir.mkdir()

        yaml_file = invalid_dir / "challenge.yaml"
        yaml_file.write_text("invalid: yaml: :")

        loader = ChallengeLoaderService(db_session, str(challenges_dir))

        with pytest.raises(ValueError, match="Failed to preload"):
            await loader.preload_all_challenges()


class TestListChallenges:
    """Test listing challenges with filters."""

    @pytest.mark.asyncio
    async def test_list_all_challenges(self, db_session, challenge_loader):
        """Test listing all challenges without filters."""
        # Add test challenges
        challenges = [
            Challenge(
                id=f"test-{i}",
                name=f"Test {i}",
                difficulty="easy" if i % 2 == 0 else "hard",
                task_type="coding",
                config_yaml=f"id: test-{i}",
                created_at=datetime.utcnow()
            )
            for i in range(1, 4)
        ]

        for c in challenges:
            db_session.add(c)
        await db_session.commit()

        result = await challenge_loader.list_challenges()

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_list_by_difficulty(self, db_session, challenge_loader):
        """Test filtering challenges by difficulty."""
        challenges = [
            Challenge(
                id="easy-1", name="Easy", difficulty="easy",
                task_type="coding", config_yaml="id: easy-1",
                created_at=datetime.utcnow()
            ),
            Challenge(
                id="hard-1", name="Hard", difficulty="hard",
                task_type="coding", config_yaml="id: hard-1",
                created_at=datetime.utcnow()
            ),
        ]

        for c in challenges:
            db_session.add(c)
        await db_session.commit()

        easy_challenges = await challenge_loader.list_challenges(difficulty="easy")

        assert len(easy_challenges) == 1
        assert easy_challenges[0].difficulty == "easy"

    @pytest.mark.asyncio
    async def test_list_by_task_type(self, db_session, challenge_loader):
        """Test filtering challenges by task type."""
        challenges = [
            Challenge(
                id="code-1", name="Code", difficulty="easy",
                task_type="coding", config_yaml="id: code-1",
                created_at=datetime.utcnow()
            ),
            Challenge(
                id="extract-1", name="Extract", difficulty="easy",
                task_type="extraction", config_yaml="id: extract-1",
                created_at=datetime.utcnow()
            ),
        ]

        for c in challenges:
            db_session.add(c)
        await db_session.commit()

        coding_challenges = await challenge_loader.list_challenges(task_type="coding")

        assert len(coding_challenges) == 1
        assert coding_challenges[0].task_type == "coding"


class TestClearCache:
    """Test cache clearing functionality."""

    @pytest.mark.asyncio
    async def test_clear_cache(self, db_session, challenge_loader):
        """Test clearing in-memory cache."""
        # Populate cache
        challenge_loader._cache["test-1"] = Challenge(
            id="test-1", name="Test",
            difficulty="easy", task_type="coding",
            config_yaml="id: test-1",
            created_at=datetime.utcnow()
        )

        assert len(challenge_loader._cache) > 0

        challenge_loader.clear_cache()

        assert len(challenge_loader._cache) == 0


class TestLoadCourses:
    """Test course loading from courses.yaml."""

    @pytest.mark.asyncio
    async def test_load_courses_success(self, db_session, challenge_loader):
        """Test successful course loading."""
        if Path(challenge_loader._challenges_dir / "courses.yaml").exists():
            courses = await challenge_loader.load_courses()

            assert len(courses) > 0
            assert isinstance(courses, dict)

    @pytest.mark.asyncio
    async def test_load_courses_caching(self, db_session, challenge_loader):
        """Test that courses are cached after first load."""
        if Path(challenge_loader._challenges_dir / "courses.yaml").exists():
            courses1 = await challenge_loader.load_courses()
            assert len(challenge_loader._courses_cache) > 0

            # Second call should use cache
            courses2 = await challenge_loader.load_courses()
            assert courses1 == courses2

    @pytest.mark.asyncio
    async def test_load_courses_missing_file(self, db_session, tmp_path):
        """Test course loading with missing file raises error."""
        loader = ChallengeLoaderService(db_session, str(tmp_path))

        with pytest.raises(FileNotFoundError, match="Courses file not found"):
            await loader.load_courses()

    @pytest.mark.asyncio
    async def test_load_courses_invalid_yaml(self, db_session, tmp_path):
        """Test course loading with invalid YAML raises error."""
        courses_file = tmp_path / "courses.yaml"
        courses_file.write_text("invalid: yaml: :")

        loader = ChallengeLoaderService(db_session, str(tmp_path))

        with pytest.raises(ValueError, match="Invalid YAML"):
            await loader.load_courses()

    @pytest.mark.asyncio
    async def test_load_courses_missing_key(self, db_session, tmp_path):
        """Test course loading with missing 'courses' key raises error."""
        courses_file = tmp_path / "courses.yaml"
        courses_file.write_text("other_key: value")

        loader = ChallengeLoaderService(db_session, str(tmp_path))

        with pytest.raises(ValueError, match="missing 'courses' key"):
            await loader.load_courses()


class TestGetCourse:
    """Test individual course retrieval."""

    @pytest.mark.asyncio
    async def test_get_existing_course(self, db_session, challenge_loader):
        """Test getting a course by ID."""
        if Path(challenge_loader._challenges_dir / "courses.yaml").exists():
            course = await challenge_loader.get_course("beginner-course")

            if course:
                assert course["id"] == "beginner-course"
                assert "name" in course
                assert "holes" in course

    @pytest.mark.asyncio
    async def test_get_nonexistent_course(self, db_session, challenge_loader):
        """Test getting nonexistent course returns None."""
        # Ensure courses are loaded
        if Path(challenge_loader._challenges_dir / "courses.yaml").exists():
            await challenge_loader.load_courses()

        course = await challenge_loader.get_course("nonexistent-course")
        assert course is None


class TestCourseValidation:
    """Test course configuration validation."""

    @pytest.mark.asyncio
    async def test_validate_valid_course(self, db_session, tmp_path):
        """Test validation accepts valid course config."""
        courses_file = tmp_path / "courses.yaml"
        valid_config = {
            "courses": [
                {
                    "id": "test-course",
                    "name": "Test Course",
                    "description": "Test",
                    "difficulty": "easy",
                    "holes": ["hole-001"],
                }
            ]
        }
        courses_file.write_text(yaml.dump(valid_config))

        loader = ChallengeLoaderService(db_session, str(tmp_path))
        courses = await loader.load_courses()

        assert "test-course" in courses

    @pytest.mark.asyncio
    async def test_validate_missing_required_field(self, db_session, tmp_path):
        """Test validation rejects course missing required fields."""
        courses_file = tmp_path / "courses.yaml"
        invalid_config = {
            "courses": [
                {
                    "id": "test-course",
                    # Missing name, description, difficulty, holes
                }
            ]
        }
        courses_file.write_text(yaml.dump(invalid_config))

        loader = ChallengeLoaderService(db_session, str(tmp_path))

        with pytest.raises(ValueError, match="missing required field"):
            await loader.load_courses()

    @pytest.mark.asyncio
    async def test_validate_empty_holes(self, db_session, tmp_path):
        """Test validation rejects course with empty holes list."""
        courses_file = tmp_path / "courses.yaml"
        invalid_config = {
            "courses": [
                {
                    "id": "test-course",
                    "name": "Test",
                    "description": "Test",
                    "difficulty": "easy",
                    "holes": [],
                }
            ]
        }
        courses_file.write_text(yaml.dump(invalid_config))

        loader = ChallengeLoaderService(db_session, str(tmp_path))

        with pytest.raises(ValueError, match="cannot be empty"):
            await loader.load_courses()

    @pytest.mark.asyncio
    async def test_validate_invalid_difficulty(self, db_session, tmp_path):
        """Test validation rejects invalid difficulty."""
        courses_file = tmp_path / "courses.yaml"
        invalid_config = {
            "courses": [
                {
                    "id": "test-course",
                    "name": "Test",
                    "description": "Test",
                    "difficulty": "invalid",
                    "holes": ["hole-001"],
                }
            ]
        }
        courses_file.write_text(yaml.dump(invalid_config))

        loader = ChallengeLoaderService(db_session, str(tmp_path))

        with pytest.raises(ValueError, match="invalid difficulty"):
            await loader.load_courses()


class TestChallengeValidation:
    """Test challenge YAML validation."""

    @pytest.mark.asyncio
    async def test_validate_missing_id(self, db_session, tmp_path):
        """Test validation rejects challenge missing ID."""
        challenges_dir = tmp_path / "challenges"
        challenges_dir.mkdir()

        challenge_dir = challenges_dir / "test-001"
        challenge_dir.mkdir()

        yaml_file = challenge_dir / "challenge.yaml"
        yaml_file.write_text(yaml.dump({
            "name": "Test",
            "description": "Test",
            "task_type": "coding",
            "validation": {"type": "test_cases"},
        }))

        loader = ChallengeLoaderService(db_session, str(challenges_dir))

        with pytest.raises(ValueError, match="missing required field"):
            await loader.preload_all_challenges()

    @pytest.mark.asyncio
    async def test_validate_id_mismatch(self, db_session, tmp_path):
        """Test validation rejects ID mismatch with directory."""
        challenges_dir = tmp_path / "challenges"
        challenges_dir.mkdir()

        challenge_dir = challenges_dir / "test-001"
        challenge_dir.mkdir()

        yaml_file = challenge_dir / "challenge.yaml"
        yaml_file.write_text(yaml.dump({
            "id": "wrong-id",
            "name": "Test",
            "description": "Test",
            "task_type": "coding",
            "validation": {"type": "test_cases"},
        }))

        loader = ChallengeLoaderService(db_session, str(challenges_dir))

        with pytest.raises(ValueError, match="ID mismatch"):
            await loader.preload_all_challenges()

    @pytest.mark.asyncio
    async def test_validate_invalid_task_type(self, db_session, tmp_path):
        """Test validation rejects invalid task type."""
        challenges_dir = tmp_path / "challenges"
        challenges_dir.mkdir()

        challenge_dir = challenges_dir / "test-001"
        challenge_dir.mkdir()

        yaml_file = challenge_dir / "challenge.yaml"
        yaml_file.write_text(yaml.dump({
            "id": "test-001",
            "name": "Test",
            "description": "Test",
            "task_type": "invalid_type",
            "validation": {"type": "test_cases"},
        }))

        loader = ChallengeLoaderService(db_session, str(challenges_dir))

        with pytest.raises(ValueError, match="invalid task_type"):
            await loader.preload_all_challenges()

    @pytest.mark.asyncio
    async def test_validate_invalid_validation_type(self, db_session, tmp_path):
        """Test validation rejects invalid validation type."""
        challenges_dir = tmp_path / "challenges"
        challenges_dir.mkdir()

        challenge_dir = challenges_dir / "test-001"
        challenge_dir.mkdir()

        yaml_file = challenge_dir / "challenge.yaml"
        yaml_file.write_text(yaml.dump({
            "id": "test-001",
            "name": "Test",
            "description": "Test",
            "task_type": "coding",
            "validation": {"type": "invalid_validation"},
        }))

        loader = ChallengeLoaderService(db_session, str(challenges_dir))

        with pytest.raises(ValueError, match="invalid validation.type"):
            await loader.preload_all_challenges()
