"""Who may call the server over HTTP, and what each caller may do.

The demo reads two tokens from the environment. In production, verify a JWT
from your identity provider here instead: its signature, expiry and audience.
"""

import hmac
import os

from mcp.server.auth.provider import AccessToken

READ = "tickets:read"
WRITE = "tickets:write"


class DemoTokenVerifier:
    """Maps a bearer token to the scopes it grants, or rejects it."""

    async def verify_token(self, token: str) -> AccessToken | None:
        known = {
            os.environ["TICKETS_READ_TOKEN"]: [READ],
            os.environ["TICKETS_WRITE_TOKEN"]: [READ, WRITE],
        }
        for secret, scopes in known.items():
            # Constant-time comparison, so response timing leaks nothing.
            if hmac.compare_digest(token, secret):
                return AccessToken(token=token, client_id="demo", scopes=scopes)
        return None
