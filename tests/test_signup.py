def test_signup_adds_student_to_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_duplicate_email_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_when_activity_is_full_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    activities_response = client.get("/activities")
    activity = activities_response.json()[activity_name]
    remaining_spots = activity["max_participants"] - len(activity["participants"])

    for index in range(remaining_spots):
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": f"fill{index}@mergington.edu"},
        )

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "overflow@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_when_full_does_not_add_participant(client):
    # Arrange
    activity_name = "Chess Club"
    activities_response = client.get("/activities")
    activity = activities_response.json()[activity_name]
    remaining_spots = activity["max_participants"] - len(activity["participants"])

    for index in range(remaining_spots):
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": f"capacity{index}@mergington.edu"},
        )

    # Act
    rejected_email = "notadded@mergington.edu"
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": rejected_email},
    )
    final_state = client.get("/activities").json()[activity_name]

    # Assert
    assert response.status_code == 400
    assert rejected_email not in final_state["participants"]
    assert len(final_state["participants"]) == final_state["max_participants"]
