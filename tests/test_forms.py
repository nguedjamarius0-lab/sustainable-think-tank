from werkzeug.datastructures import MultiDict
from flask_wtf.csrf import generate_csrf
from app.forms import (
    RegisterForm, LoginForm, ContactForm, NewsletterForm,
    JoinApplicationForm, TeamStep1Form, TeamStep2Form
)


def _make_formdata(**kwargs):
    kwargs["csrf_token"] = generate_csrf()
    return MultiDict(kwargs)


def test_register_form_validation(app):
    with app.test_request_context():
        form = RegisterForm(_make_formdata(
            name="Test User",
            email="test@test.com",
            password="password123",
            confirm_password="password123"
        ))
        assert form.validate()


def test_register_form_password_mismatch(app):
    with app.test_request_context():
        form = RegisterForm(_make_formdata(
            name="Test User",
            email="test@test.com",
            password="password123",
            confirm_password="differentpassword"
        ))
        assert not form.validate()


def test_contact_form_validation(app):
    with app.test_request_context():
        form = ContactForm(_make_formdata(
            name="Test User",
            email="test@test.com",
            subject="Test Subject",
            message="This is a test message with enough content."
        ))
        assert form.validate()


def test_newsletter_form_validation(app):
    with app.test_request_context():
        form = NewsletterForm(_make_formdata(email="test@test.com"))
        assert form.validate()


def test_join_form_validation(app):
    with app.test_request_context():
        form = JoinApplicationForm(_make_formdata(
            name="Test User",
            email="test@test.com",
            application_type="chercheur"
        ))
        assert form.validate()


def test_team_step1_form(app):
    with app.test_request_context():
        form = TeamStep1Form(_make_formdata(
            name="Test Team",
            theme="Économie"
        ))
        assert form.validate()


def test_team_step2_form(app):
    with app.test_request_context():
        form = TeamStep2Form(_make_formdata(member_count="5"))
        assert form.validate()

        form_invalid = TeamStep2Form(_make_formdata(member_count="25"))
        assert not form_invalid.validate()
