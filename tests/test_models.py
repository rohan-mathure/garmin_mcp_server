import pytest
from pydantic import ValidationError

from garmin_mcp.models import CredentialsInput, MFAInput


def test_credentials_input_valid():
    creds = CredentialsInput(email="user@example.com", password="secret")
    assert creds.email == "user@example.com"
    assert creds.password == "secret"


def test_mfa_input_valid():
    mfa = MFAInput(code="123456")
    assert mfa.code == "123456"


def test_credentials_input_missing_email():
    with pytest.raises(ValidationError):
        CredentialsInput(password="secret")


def test_credentials_input_missing_password():
    with pytest.raises(ValidationError):
        CredentialsInput(email="user@example.com")


def test_credentials_input_missing_both():
    with pytest.raises(ValidationError):
        CredentialsInput()


def test_mfa_input_missing_code():
    with pytest.raises(ValidationError):
        MFAInput()
