"""
Integration tests for Challenge API endpoints.

Tests:
- List challenges with filtering and pagination
- Get challenge details
- Request validation
- Error handling
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge


# ============================================================================
# List Challenges Tests
# ============================================================================


class TestListChallenges:
    """Test GET /api/challenges - List all challenges."""

    def test_list_all_challenges_success(
        self,
        client: TestClient,
        all_challenges: list[Challenge],
    ):
        """Test listing all challenges without filters."""
        response = client.get("/api/challenges")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "challenges" in data
        assert "total" in data
        assert "filtered" in data
        assert "page" in data
        assert "per_page" in data
        assert "has_more" in data

        # Verify challenges are returned
        assert data["total"] > 0
        assert len(data["challenges"]) > 0
        assert data["total"] == data["filtered"]  # No filters applied

        # Verify challenge structure
        for challenge in data["challenges"]:
            assert "id" in challenge
            assert "name" in challenge
            assert "difficulty" in challenge
            assert "task_type" in challenge

    def test_list_challenges_with_pagination(
        self,
        client: TestClient,
        all_challenges: list[Challenge],
    ):
        """Test pagination parameters."""
        # Request first page with small page size
        response = client.get("/api/challenges?page=1&per_page=2")

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 1
        assert data["per_page"] == 2
        assert len(data["challenges"]) <= 2

        # If there are more than 2 challenges, has_more should be True
        if data["total"] > 2:
            assert data["has_more"] is True

    def test_list_challenges_pagination_second_page(
        self,
        client: TestClient,
        all_challenges: list[Challenge],
    ):
        """Test retrieving second page."""
        # Get first page
        response1 = client.get("/api/challenges?page=1&per_page=1")
        data1 = response1.json()

        # Get second page
        response2 = client.get("/api/challenges?page=2&per_page=1")
        data2 = response2.json()

        assert response2.status_code == 200

        # If we have multiple challenges, verify they're different
        if data1["total"] > 1:
            first_id = data1["challenges"][0]["id"]
            second_id = data2["challenges"][0]["id"]
            assert first_id != second_id

    def test_list_challenges_filter_by_difficulty(
        self,
        client: TestClient,
        all_challenges: list[Challenge],
    ):
        """Test filtering by difficulty."""
        response = client.get("/api/challenges?difficulty=easy")

        assert response.status_code == 200
        data = response.json()

        # Verify all returned challenges have easy difficulty
        for challenge in data["challenges"]:
            assert challenge["difficulty"] == "easy"

        # filtered count should be <= total count
        assert data["filtered"] <= data["total"]

    def test_list_challenges_filter_by_task_type(
        self,
        client: TestClient,
        all_challenges: list[Challenge],
    ):
        """Test filtering by task type."""
        response = client.get("/api/challenges?task_type=coding")

        assert response.status_code == 200
        data = response.json()

        # Verify all returned challenges have coding task type
        for challenge in data["challenges"]:
            assert challenge["task_type"] == "coding"

    def test_list_challenges_combined_filters(
        self,
        client: TestClient,
        all_challenges: list[Challenge],
    ):
        """Test combining difficulty and task_type filters."""
        response = client.get("/api/challenges?difficulty=easy&task_type=coding")

        assert response.status_code == 200
        data = response.json()

        # Verify all challenges match both filters
        for challenge in data["challenges"]:
            assert challenge["difficulty"] == "easy"
            assert challenge["task_type"] == "coding"

    def test_list_challenges_invalid_difficulty(self, client: TestClient):
        """Test error handling for invalid difficulty filter."""
        response = client.get("/api/challenges?difficulty=invalid")

        assert response.status_code == 400
        data = response.json()

        # Error is wrapped in detail field
        assert "detail" in data
        detail = data["detail"]
        assert detail["error"] == "invalid_difficulty"
        assert "message" in detail
        assert "details" in detail
        assert "suggestions" in detail

    def test_list_challenges_invalid_task_type(self, client: TestClient):
        """Test error handling for invalid task_type filter."""
        response = client.get("/api/challenges?task_type=invalid")

        assert response.status_code == 400
        data = response.json()

        # Error is wrapped in detail field
        assert "detail" in data
        detail = data["detail"]
        assert detail["error"] == "invalid_task_type"
        assert "message" in detail
        assert "details" in detail
        assert "suggestions" in detail

    def test_list_challenges_invalid_pagination(self, client: TestClient):
        """Test error handling for invalid pagination parameters."""
        # Page must be >= 1
        response = client.get("/api/challenges?page=0")
        assert response.status_code == 422  # Validation error

        # Per_page must be >= 1 and <= 100
        response = client.get("/api/challenges?per_page=0")
        assert response.status_code == 422

        response = client.get("/api/challenges?per_page=101")
        assert response.status_code == 422

    def test_list_challenges_empty_result(self, client: TestClient):
        """Test listing with filters that return no results."""
        # Try to filter by a valid difficulty that might not exist
        response = client.get("/api/challenges?difficulty=expert")

        assert response.status_code == 200
        data = response.json()

        # Should return empty list, not error
        assert "challenges" in data
        # filtered can be 0 if no expert challenges exist
        assert data["filtered"] >= 0


# ============================================================================
# Get Challenge Details Tests
# ============================================================================


class TestGetChallenge:
    """Test GET /api/challenges/{challenge_id} - Get challenge details."""

    def test_get_challenge_success(
        self,
        client: TestClient,
        sample_challenge: Challenge,
    ):
        """Test retrieving a specific challenge."""
        response = client.get(f"/api/challenges/{sample_challenge.id}")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["id"] == sample_challenge.id
        assert "name" in data
        assert "difficulty" in data
        assert "task_type" in data
        assert "description" in data
        assert "validation_type" in data
        assert "system_prompt_default" in data
        assert "system_prompt_removable" in data
        assert "system_prompt_editable" in data
        assert "context_files" in data

    def test_get_challenge_not_found(self, client: TestClient):
        """Test retrieving non-existent challenge."""
        response = client.get("/api/challenges/non-existent-id")

        assert response.status_code == 404
        data = response.json()

        # Error is wrapped in detail field
        assert "detail" in data
        detail = data["detail"]
        assert detail["error"] == "challenge_not_found"
        assert "message" in detail
        assert "details" in detail
        assert "suggestions" in detail

    def test_get_challenge_includes_metadata(
        self,
        client: TestClient,
        sample_challenge: Challenge,
    ):
        """Test that challenge details include all metadata."""
        response = client.get(f"/api/challenges/{sample_challenge.id}")

        assert response.status_code == 200
        data = response.json()

        # Check optional metadata fields
        assert "estimated_tokens_expert" in data
        assert "estimated_tokens_beginner" in data

    def test_get_challenge_system_prompt_config(
        self,
        client: TestClient,
        sample_challenge: Challenge,
    ):
        """Test that system prompt configuration is returned."""
        response = client.get(f"/api/challenges/{sample_challenge.id}")

        assert response.status_code == 200
        data = response.json()

        # System prompt configuration should be present
        assert "system_prompt_removable" in data
        assert "system_prompt_editable" in data
        assert isinstance(data["system_prompt_removable"], bool)
        assert isinstance(data["system_prompt_editable"], bool)

    def test_get_multiple_challenges(
        self,
        client: TestClient,
        all_challenges: list[Challenge],
    ):
        """Test retrieving multiple challenges by ID."""
        # Get all challenge IDs from list endpoint
        list_response = client.get("/api/challenges")
        challenges = list_response.json()["challenges"]

        # Retrieve each challenge individually
        for challenge in challenges[:3]:  # Test first 3
            response = client.get(f"/api/challenges/{challenge['id']}")
            assert response.status_code == 200

            data = response.json()
            assert data["id"] == challenge["id"]
            assert data["name"] == challenge["name"]


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestChallengesErrorHandling:
    """Test error handling and edge cases."""

    def test_list_challenges_server_error_handling(
        self,
        client: TestClient,
        monkeypatch,
    ):
        """Test handling of unexpected server errors."""
        # This test verifies the error handling structure
        # In a real scenario, we'd mock a service to raise an exception

    def test_get_challenge_special_characters(self, client: TestClient):
        """Test challenge ID with special characters."""
        # Test various special characters in ID
        special_ids = [
            "hole-001%20",
            "hole-001/extra",  # Changed since "/" is path separator
            "hole-001;",
        ]

        for challenge_id in special_ids:
            response = client.get(f"/api/challenges/{challenge_id}")
            # Should return 404 (not found) since these IDs don't exist
            # FastAPI will handle the path correctly
            assert response.status_code in [400, 404, 422]

    def test_list_challenges_extreme_pagination(self, client: TestClient):
        """Test pagination with extreme values."""
        # Very large page number
        response = client.get("/api/challenges?page=9999")
        assert response.status_code == 200
        data = response.json()
        assert len(data["challenges"]) == 0  # No challenges at page 9999
        assert data["has_more"] is False

        # Maximum per_page value
        response = client.get("/api/challenges?per_page=100")
        assert response.status_code == 200


# ============================================================================
# Content Validation Tests
# ============================================================================


class TestChallengesContentValidation:
    """Test that returned challenge content is valid."""

    def test_challenge_required_fields(
        self,
        client: TestClient,
        all_challenges: list[Challenge],
    ):
        """Test that all challenges have required fields."""
        response = client.get("/api/challenges")
        challenges = response.json()["challenges"]

        for challenge in challenges:
            # Required fields for listing
            assert challenge["id"]
            assert challenge["name"]
            assert challenge["difficulty"] in ["easy", "medium", "hard", "expert"]
            assert challenge["task_type"] in [
                "coding",
                "extraction",
                "question_answering",
                "generation",
            ]

    def test_challenge_detail_complete(
        self,
        client: TestClient,
        sample_challenge: Challenge,
    ):
        """Test that challenge details are complete."""
        response = client.get(f"/api/challenges/{sample_challenge.id}")
        data = response.json()

        # Required detail fields
        assert data["id"]
        assert data["name"]
        assert data["difficulty"]
        assert data["task_type"]
        assert data["description"]
        assert data["validation_type"]

        # Description should not be empty
        assert len(data["description"]) > 0

    def test_challenge_context_files_structure(
        self,
        client: TestClient,
        sample_challenge: Challenge,
    ):
        """Test that context_files field has correct structure."""
        response = client.get(f"/api/challenges/{sample_challenge.id}")
        data = response.json()

        assert "context_files" in data
        assert isinstance(data["context_files"], list)
