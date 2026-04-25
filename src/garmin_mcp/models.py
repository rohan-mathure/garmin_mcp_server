from pydantic import BaseModel


class MFAInput(BaseModel):
    code: str
    """One-time password from your authenticator app or SMS"""


class CredentialsInput(BaseModel):
    email: str
    """Garmin Connect account email"""
    password: str
    """Garmin Connect account password"""
