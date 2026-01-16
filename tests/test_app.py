"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    # Store initial state
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and inter-school games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 10,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore topics in physics, chemistry, and biology",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["liam@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills through competitive debate",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["charlotte@mergington.edu", "benjamin@mergington.edu"]
        }
    }
    
    yield
    
    # Reset to initial state after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_get_activities_contains_activity_details(self, client):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_contains_participants(self, client):
        """Test that participants list is populated"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert isinstance(activity["participants"], list)
        assert "michael@mergington.edu" in activity["participants"]


class TestSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds participant to activity"""
        # Get initial participants
        initial = client.get("/activities").json()
        initial_count = len(initial["Chess Club"]["participants"])
        
        # Sign up new participant
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Verify participant was added
        updated = client.get("/activities").json()
        assert len(updated["Chess Club"]["participants"]) == initial_count + 1
        assert "newstudent@mergington.edu" in updated["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test signup fails if student already signed up"""
        # Try to sign up someone already in the activity
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple students can sign up for same activity"""
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"
        
        response1 = client.post(f"/activities/Chess Club/signup?email={student1}")
        response2 = client.post(f"/activities/Chess Club/signup?email={student2}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_data = client.get("/activities").json()
        assert student1 in activities_data["Chess Club"]["participants"]
        assert student2 in activities_data["Chess Club"]["participants"]


class TestUnregister:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant"""
        # Get initial count
        initial = client.get("/activities").json()
        initial_count = len(initial["Chess Club"]["participants"])
        
        # Unregister participant
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        # Verify participant was removed
        updated = client.get("/activities").json()
        assert len(updated["Chess Club"]["participants"]) == initial_count - 1
        assert "michael@mergington.edu" not in updated["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_student_not_enrolled(self, client):
        """Test unregister fails if student not enrolled"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signup followed by unregister"""
        student_email = "temporary@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Chess Club/signup?email={student_email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_data = client.get("/activities").json()
        assert student_email in activities_data["Chess Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Chess Club/unregister?email={student_email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities_data = client.get("/activities").json()
        assert student_email not in activities_data["Chess Club"]["participants"]


class TestRoot:
    """Test suite for root endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
