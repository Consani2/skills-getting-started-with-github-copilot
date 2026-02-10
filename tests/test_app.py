"""Tests for the Mergington High School Activities API"""

import pytest


def test_root_redirect(client):
    """Test that root path redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Basketball" in activities
    
    # Verify structure of an activity
    chess = activities["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_for_activity(client):
    """Test signing up a student for an activity"""
    email = "test.student@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        json={}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert email in result["message"]
    assert activity in result["message"]
    
    # Verify the student was actually added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate(client):
    """Test that a student cannot sign up twice for the same activity"""
    email = "duplicate.test@mergington.edu"
    activity = "Chess Club"
    
    # First signup should work
    response1 = client.post(
        f"/activities/{activity}/signup?email={email}",
        json={}
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        f"/activities/{activity}/signup?email={email}",
        json={}
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_invalid_activity(client):
    """Test signing up for a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Non Existent Activity"
    
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        json={}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_unregister_from_activity(client):
    """Test unregistering a student from an activity"""
    email = "unregister.test@mergington.edu"
    activity = "Programming Class"
    
    # First, sign up
    signup_response = client.post(
        f"/activities/{activity}/signup?email={email}",
        json={}
    )
    assert signup_response.status_code == 200
    
    # Verify signup
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    assert unregister_response.status_code == 200
    result = unregister_response.json()
    assert "Unregistered" in result["message"]
    assert email in result["message"]
    
    # Verify unregister
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_up(client):
    """Test unregistering when student is not signed up"""
    email = "not.signed.up@mergington.edu"
    activity = "Drama Club"
    
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_invalid_activity(client):
    """Test unregistering from a non-existent activity"""
    email = "test@mergington.edu"
    activity = "Non Existent Activity"
    
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_activity_max_participants(client):
    """Test that we can still track max_participants"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert activity_data["max_participants"] > 0
        assert len(activity_data["participants"]) <= activity_data["max_participants"]
