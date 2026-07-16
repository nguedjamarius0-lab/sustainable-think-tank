from app.models import User, Publication, Event, Video


def test_user_creation(app):
    with app.app_context():
        user = User(name="Test User", email="test@test.com", role="user")
        user.set_password("password123")
        assert user.check_password("password123")
        assert not user.check_password("wrongpassword")


def test_user_roles(app):
    with app.app_context():
        user = User(name="Test User", email="test@test.com", role="user")
        assert not user.can_publish()

        editor = User(name="Editor", email="editor@test.com", role="editor")
        assert editor.can_publish()

        admin = User(name="Admin", email="admin@test.com", role="admin")
        assert admin.can_publish()


def test_publication_slug(app):
    with app.app_context():
        slug = Publication.generate_slug("Mon Test de Publication")
        assert slug == "mon-test-de-publication"


def test_video_embed_url(app):
    with app.app_context():
        video = Video(title="Test", video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert "embed" in video.get_embed_url()

        video2 = Video(title="Test2", video_url="https://youtu.be/dQw4w9WgXcQ")
        assert "embed" in video2.get_embed_url()

        video3 = Video(title="Test3", video_url="https://vimeo.com/123456")
        assert "player.vimeo.com" in video3.get_embed_url()
