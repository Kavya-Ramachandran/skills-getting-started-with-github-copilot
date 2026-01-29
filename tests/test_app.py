"""
Tests for the Mergington High School Activities API
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for getting activities"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns 200 OK"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_has_expected_keys(self):
        """Test that activities have expected keys"""
        response = client.get("/activities")
        activities = response.json()
        
        assert len(activities) > 0
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_get_activities_contains_tennis_club(self):
        """Test that Tennis Club is in activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Tennis Club" in activities


class TestSignupForActivity:
    """Tests for signing up for activities"""

    def test_signup_returns_200(self):
        """Test that signup returns 200 OK"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant(self):
        """Test that signup adds participant to activity"""
        email = "participant@mergington.edu"
        
        # Get initial participants
        response_before = client.get("/activities")
        participants_before = response_before.json()["Tennis Club"]["participants"]
        
        # Sign up
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        
        # Get participants after signup
        response_after = client.get("/activities")
        participants_after = response_after.json()["Tennis Club"]["participants"]
        
        assert len(participants_after) == len(participants_before) + 1
        assert email in participants_after

    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_signup_duplicate_participant_returns_400(self):
        """Test that duplicate signup returns 400"""
        email = "duplicate@mergington.edu"
        
        # First signup
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        
        # Second signup with same email
        response = client.post(f"/activities/Tennis%20Club/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for unregistering from activities"""

    def test_unregister_returns_200(self):
        """Test that unregister returns 200 OK"""
        email = "unregister@mergington.edu"
        
        # First signup
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/Tennis%20Club/unregister?email={email}"
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self):
        """Test that unregister returns a success message"""
        email = "remove@mergington.edu"
        
        # First signup
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/Tennis%20Club/unregister?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from activity"""
        email = "removeme@mergington.edu"
        
        # First signup
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        
        # Get participants after signup
        response_before = client.get("/activities")
        assert email in response_before.json()["Tennis Club"]["participants"]
        
        # Then unregister
        client.delete(f"/activities/Tennis%20Club/unregister?email={email}")
        
        # Get participants after unregister
        response_after = client.get("/activities")
        assert email not in response_after.json()["Tennis Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregister for nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_nonexistent_participant_returns_400(self):
        """Test that unregister for nonexistent participant returns 400"""
        response = client.delete(
            "/activities/Tennis%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400


class TestRootRedirect:
    """Tests for root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
