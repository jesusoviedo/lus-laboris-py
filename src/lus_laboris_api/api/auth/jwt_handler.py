"""
JWT token validation using public key authentication
"""

import logging
import os
from typing import Any

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from ..config import settings

logger = logging.getLogger(__name__)


class JWTValidator:
    """JWT validator for token validation using RSA public key"""

    def __init__(self):
        self.public_key = None
        self.algorithm = "RS256"

        # Load public key for validation
        self._load_public_key()

    def _load_public_key(self):
        """Load public key from file for token validation"""
        public_key_path = settings.api_jwt_public_key_path

        # Resolve path relative to project root if needed
        if not os.path.isabs(public_key_path):
            # Get project root (assuming this file is in src/lus_laboris_api/api/auth/)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
            public_key_path = os.path.join(project_root, public_key_path)

        try:
            with open(public_key_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(), backend=default_backend()
                )
            logger.info(f"JWT public key loaded successfully from {public_key_path}")
        except FileNotFoundError:
            logger.error(f"JWT public key not found at {public_key_path}")
            raise ValueError(
                "JWT public key not found. Please ensure the key file exists at {public_key_path}"
            )
        except Exception as e:
            logger.error(f"Failed to load JWT public key: {e!s}")
            raise ValueError(f"Failed to load JWT public key: {e!s}")

    def validate_token(self, token: str) -> dict[str, Any]:
        """Validate a JWT token and return its payload"""
        if not self.public_key:
            raise ValueError("Public key not available for token validation")

        try:
            # Get expected issuer and audience from settings
            expected_issuer = settings.api_jwt_iss
            expected_audience = settings.api_jwt_aud

            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                audience=expected_audience,  # Validate audience from config
                issuer=expected_issuer,  # Validate issuer from config
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )

            logger.info(f"JWT token validated for subject: {payload.get('sub', 'unknown')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise ValueError("Token has expired")
        except jwt.InvalidAudienceError:
            logger.warning(f"Invalid JWT audience. Expected: {expected_audience}")
            raise ValueError(f"Invalid audience. Expected: {expected_audience}")
        except jwt.InvalidIssuerError:
            logger.warning(f"Invalid JWT issuer. Expected: {expected_issuer}")
            raise ValueError(f"Invalid issuer. Expected: {expected_issuer}")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e!s}")
            raise ValueError(f"Invalid token: {e!s}")

    def get_public_key_pem(self) -> str:
        """Get the public key in PEM format for external validation"""
        if not self.public_key:
            raise ValueError("Public key not available")

        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    def is_token_valid(self, token: str) -> bool:
        """Check if a token is valid without raising exceptions"""
        try:
            self.validate_token(token)
            return True
        except ValueError:
            return False


# Global instance
jwt_validator = JWTValidator()
