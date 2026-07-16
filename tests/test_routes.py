def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Tendereo" in response.data


def test_publications(client):
    response = client.get("/publications/")
    assert response.status_code == 200


def test_events(client):
    response = client.get("/evenements/")
    assert response.status_code == 200


def test_team(client):
    response = client.get("/equipe/")
    assert response.status_code == 200


def test_contact(client):
    response = client.get("/contact/")
    assert response.status_code == 200


def test_media(client):
    response = client.get("/medias/")
    assert response.status_code == 200


def test_reseau(client):
    response = client.get("/reseaux/")
    assert response.status_code == 200


def test_join(client):
    response = client.get("/agir/")
    assert response.status_code == 200


def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "Connexion" in response.data.decode()


def test_register_page(client):
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert "Créer un compte" in response.data.decode()


def test_admin_redirect(client):
    response = client.get("/admin/")
    assert response.status_code == 302


def test_login_success(client, app):
    with app.app_context():
        from app.models import User
        user = User(name="Test", email="test@test.com", role="user", is_verified=True)
        user.set_password("password123")
        from app import db
        db.session.add(user)
        db.session.commit()

    response = client.post("/auth/login", data={
        "email": "test@test.com",
        "password": "password123",
        "csrf_token": "skip"
    }, follow_redirects=True)
    assert response.status_code == 200


def test_login_failure(client):
    response = client.post("/auth/login", data={
        "email": "wrong@test.com",
        "password": "wrongpassword",
        "csrf_token": "skip"
    }, follow_redirects=True)
    assert response.status_code == 200


def test_register_success(client):
    response = client.post("/auth/register", data={
        "name": "New User",
        "email": "new@test.com",
        "password": "password123",
        "confirm_password": "password123",
        "csrf_token": "skip"
    }, follow_redirects=True)
    assert response.status_code == 200


def test_contact_form(client):
    response = client.post("/contact/", data={
        "name": "Test User",
        "email": "test@test.com",
        "subject": "Test Subject",
        "message": "This is a test message with enough content.",
        "csrf_token": "skip"
    }, follow_redirects=True)
    assert response.status_code == 200


def test_newsletter_subscription(client):
    response = client.post("/contact/newsletter", data={
        "email": "newsletter@test.com",
        "csrf_token": "skip"
    }, follow_redirects=True)
    assert response.status_code == 200


def test_set_language(client):
    response = client.get("/set-language/en")
    assert response.status_code == 302

    response = client.get("/set-language/fr")
    assert response.status_code == 302
