"""Tests for Milestone 1: Health, Auth, Session CRUD, Audit."""


class TestHealth:
    """Test health check endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert data["data"]["checks"]["app"] == "ok"
        assert data["data"]["checks"]["database"] == "ok"
        assert "request_id" in data


class TestAuth:
    """Test authentication endpoints."""

    def test_register_user(self, client):
        response = client.post("/auth/register", json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "password123",
            "full_name": "New User",
            "role": "officer",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "newuser"
        assert data["data"]["role"] == "officer"

    def test_register_duplicate_username(self, client):
        # First registration
        client.post("/auth/register", json={
            "username": "dupuser",
            "email": "dup1@test.com",
            "password": "password123",
        })
        # Duplicate
        response = client.post("/auth/register", json={
            "username": "dupuser",
            "email": "dup2@test.com",
            "password": "password123",
        })
        assert response.status_code == 400

    def test_login_valid(self, client):
        # Register first
        client.post("/auth/register", json={
            "username": "loginuser",
            "email": "login@test.com",
            "password": "password123",
        })
        # Login
        response = client.post("/auth/login", json={
            "username": "loginuser",
            "password": "password123",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["user"]["username"] == "loginuser"

    def test_login_invalid(self, client):
        response = client.post("/auth/login", json={
            "username": "nonexistent",
            "password": "wrongpass",
        })
        assert response.status_code == 401

    def test_get_me(self, client, auth_headers):
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "testuser"

    def test_get_me_no_auth(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestScreening:
    """Test screening session CRUD."""

    def test_create_session(self, client, auth_headers):
        response = client.post(
            "/screening/create",
            json={"notes": "Test session"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "created"
        assert "id" in data["data"]

    def test_get_session(self, client, auth_headers):
        # Create
        create_resp = client.post(
            "/screening/create",
            json={"notes": "Detail test"},
            headers=auth_headers,
        )
        session_id = create_resp.json()["data"]["id"]

        # Get
        response = client.get(f"/screening/{session_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == session_id
        assert data["data"]["documents"] == []
        assert data["data"]["evidence"] == []

    def test_get_session_not_found(self, client, auth_headers):
        response = client.get("/screening/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_list_sessions(self, client, auth_headers):
        # Create a session
        client.post(
            "/screening/create",
            json={"notes": "List test"},
            headers=auth_headers,
        )

        response = client.get("/screening", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_create_session_no_auth(self, client):
        response = client.post("/screening/create", json={})
        assert response.status_code == 401


class TestAudit:
    """Test audit trail endpoints."""

    def test_audit_trail_created_on_session(self, client, auth_headers):
        # Create session
        create_resp = client.post(
            "/screening/create",
            json={"notes": "Audit test"},
            headers=auth_headers,
        )
        session_id = create_resp.json()["data"]["id"]

        # Check audit
        response = client.get(f"/audit/{session_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
        assert data["data"][0]["event_type"] == "session_created"

    def test_audit_verify(self, client, auth_headers):
        # Create session
        create_resp = client.post(
            "/screening/create",
            json={"notes": "Verify test"},
            headers=auth_headers,
        )
        session_id = create_resp.json()["data"]["id"]

        # Verify chain
        response = client.get(f"/audit/{session_id}/verify", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["valid"] is True


class TestAPIEnvelope:
    """Test API response format compliance."""

    def test_response_has_envelope(self, client):
        response = client.get("/health")
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "request_id" in data
