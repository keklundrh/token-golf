"""
Token Golf - Course Loader Service

Loads course definitions from courses.yaml and provides course-to-challenge mappings.
"""

import logging
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CourseDefinition(BaseModel):
    """A course definition from courses.yaml."""

    id: str
    name: str
    description: str
    difficulty: str
    holes: List[str] = Field(..., description="List of challenge IDs in this course")
    estimated_duration_minutes: int
    metadata: dict = Field(default_factory=dict)


class CourseLoaderService:
    """Service for loading and querying course definitions."""

    def __init__(self, challenges_dir: Path):
        """
        Initialize the course loader.

        Args:
            challenges_dir: Path to the challenges directory containing courses.yaml
        """
        self.challenges_dir = Path(challenges_dir)
        self.courses_file = self.challenges_dir / "courses.yaml"
        self._courses_cache: Optional[List[CourseDefinition]] = None

    def load_courses(self) -> List[CourseDefinition]:
        """
        Load all course definitions from courses.yaml.

        Returns:
            List of CourseDefinition objects

        Raises:
            FileNotFoundError: If courses.yaml doesn't exist
            ValueError: If courses.yaml is invalid
        """
        if self._courses_cache is not None:
            return self._courses_cache

        if not self.courses_file.exists():
            raise FileNotFoundError(
                f"courses.yaml not found at {self.courses_file}"
            )

        try:
            with open(self.courses_file, "r") as f:
                data = yaml.safe_load(f)

            if not data or "courses" not in data:
                raise ValueError("courses.yaml must contain a 'courses' key")

            courses = []
            for course_data in data["courses"]:
                courses.append(CourseDefinition(**course_data))

            self._courses_cache = courses
            logger.info(f"Loaded {len(courses)} courses from {self.courses_file}")
            return courses

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in courses.yaml: {e}")
        except Exception as e:
            raise ValueError(f"Error loading courses.yaml: {e}")

    def get_course(self, course_id: str) -> Optional[CourseDefinition]:
        """
        Get a course by ID.

        Args:
            course_id: The course identifier

        Returns:
            CourseDefinition if found, None otherwise
        """
        courses = self.load_courses()
        return next((c for c in courses if c.id == course_id), None)

    def get_course_challenges(self, course_id: str) -> List[str]:
        """
        Get the list of challenge IDs for a course.

        Args:
            course_id: The course identifier

        Returns:
            List of challenge IDs in order, or empty list if course not found
        """
        course = self.get_course(course_id)
        if course is None:
            logger.warning(f"Course '{course_id}' not found")
            return []

        return course.holes

    def list_course_ids(self) -> List[str]:
        """
        Get a list of all available course IDs.

        Returns:
            List of course IDs
        """
        courses = self.load_courses()
        return [c.id for c in courses]

    def validate_course_id(self, course_id: str) -> bool:
        """
        Check if a course ID is valid.

        Args:
            course_id: The course identifier to validate

        Returns:
            True if the course exists, False otherwise
        """
        return course_id in self.list_course_ids()
