import re

_EMAIL_RE   = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
_UNAME_RE   = re.compile(r"^[A-Za-z0-9_]{3,30}$")


def validate_email(email: str) -> bool:
    """Simple RFC-5322-ish email check."""
    return bool(email and _EMAIL_RE.match(email))


def validate_password(password: str) -> bool:
    """Minimum 8 chars (no complexity rules for MVP)."""
    return bool(password and len(password) >= 8)


def validate_location(location: dict | None) -> bool:
    """
    Ensure a JSON location has the required keys.
    Expected shape: {"latitude": float, "longitude": float, "address": str}
    """
    if not isinstance(location, dict):
        return False
    return all(k in location for k in ("latitude", "longitude", "address"))


def validate_username(username: str) -> bool:
    """3–30 chars, alphanumeric + underscore only."""
    return bool(username and _UNAME_RE.match(username))

def validate_bio(bio: str) -> bool:
    return bool(bio)
