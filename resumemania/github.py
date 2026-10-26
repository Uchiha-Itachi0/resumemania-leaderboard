"""GitHub usernames are the student identity: unique, public and easy to remember."""

from __future__ import annotations

import re

# GitHub rules: 1 to 39 chars, letters, digits and single hyphens, no leading or trailing hyphen.
USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")
PROFILE_RE = re.compile(r"github\.com/([A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38})(?![\w-])", re.IGNORECASE)
RESERVED = {"orgs", "settings", "features", "about", "pricing", "login", "join", "topics", "sponsors"}


class InvalidUsername(ValueError):
    """The message is safe to show."""


def normalise(raw: str) -> str:
    """Return the username as typed (minus @ or URL), or raise InvalidUsername."""
    value = raw.strip()
    found = PROFILE_RE.search(value)
    if found:
        value = found.group(1)
    value = value.lstrip("@").strip("/")
    if not USERNAME_RE.match(value) or value.lower() in RESERVED:
        raise InvalidUsername("Enter your GitHub username, like octocat. Letters, numbers and single hyphens only.")
    return value


def key(username: str) -> str:
    """GitHub usernames are case-insensitive, so compare in lower case."""
    return username.lower()


def from_resume(text: str) -> str | None:
    """The first github.com/<username> link in a resume, if any."""
    for match in PROFILE_RE.finditer(text):
        if match.group(1).lower() not in RESERVED:
            return match.group(1)
    return None


def avatar_url(username: str, size: int = 80) -> str:
    return f"https://github.com/{username}.png?size={size}"
