import unittest
from unittest.mock import MagicMock, patch

import jwt

from crewai_cli.authentication.utils import validate_jwt_token


def _verified_decode_raises(mock_jwt, error, unverified_claims=None):
    mock_jwt.ExpiredSignatureError = jwt.ExpiredSignatureError
    mock_jwt.InvalidAudienceError = jwt.InvalidAudienceError
    mock_jwt.InvalidIssuerError = jwt.InvalidIssuerError
    mock_jwt.MissingRequiredClaimError = jwt.MissingRequiredClaimError
    mock_jwt.InvalidTokenError = jwt.InvalidTokenError
    mock_jwt.exceptions = jwt.exceptions
    mock_jwt.decode.side_effect = [unverified_claims or {}, error]


@patch("crewai_core.auth.utils.PyJWKClient", return_value=MagicMock())
@patch("crewai_core.auth.utils.jwt")
class TestUtils(unittest.TestCase):
    def test_validate_jwt_token(self, mock_jwt, mock_pyjwkclient):
        mock_jwt.decode.return_value = {"exp": 1719859200}

        mock_pyjwkclient.return_value.get_signing_key_from_jwt.return_value = MagicMock(
            key="mock_signing_key"
        )

        jwt_token = "aaaaa.bbbbbb.cccccc"  # noqa: S105

        decoded_token = validate_jwt_token(
            jwt_token=jwt_token,
            jwks_url="https://mock_jwks_url",
            issuer="https://mock_issuer",
            audience="app_id_xxxx",
        )

        mock_jwt.decode.assert_called_with(
            jwt_token,
            "mock_signing_key",
            algorithms=["RS256"],
            audience="app_id_xxxx",
            issuer="https://mock_issuer",
            leeway=10.0,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "require": ["exp", "iat", "iss", "aud", "sub"],
            },
        )
        mock_pyjwkclient.assert_called_once_with("https://mock_jwks_url")
        self.assertEqual(decoded_token, {"exp": 1719859200})

    def test_validate_jwt_token_expired(self, mock_jwt, mock_pyjwkclient):
        _verified_decode_raises(mock_jwt, jwt.ExpiredSignatureError())
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            validate_jwt_token(
                jwt_token="aaaaa.bbbbbb.cccccc",  # noqa: S106
                jwks_url="https://mock_jwks_url",
                issuer="https://mock_issuer",
                audience="app_id_xxxx",
            )
        self.assertEqual(str(ctx.exception), "Token has expired.")

    def test_validate_jwt_token_invalid_audience(self, mock_jwt, mock_pyjwkclient):
        _verified_decode_raises(
            mock_jwt, jwt.InvalidAudienceError(), {"aud": "other_app"}
        )
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            validate_jwt_token(
                jwt_token="aaaaa.bbbbbb.cccccc",  # noqa: S106
                jwks_url="https://mock_jwks_url",
                issuer="https://mock_issuer",
                audience="app_id_xxxx",
            )
        self.assertEqual(
            str(ctx.exception),
            "Invalid token audience. Got: 'other_app'. Expected: 'app_id_xxxx'",
        )

    def test_validate_jwt_token_invalid_issuer(self, mock_jwt, mock_pyjwkclient):
        _verified_decode_raises(mock_jwt, jwt.InvalidIssuerError())
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            validate_jwt_token(
                jwt_token="aaaaa.bbbbbb.cccccc",  # noqa: S106
                jwks_url="https://mock_jwks_url",
                issuer="https://mock_issuer",
                audience="app_id_xxxx",
            )
        self.assertEqual(
            str(ctx.exception),
            "Invalid token issuer. Got: '[no issuer found]'. "
            "Expected: 'https://mock_issuer'",
        )

    def test_validate_jwt_token_missing_required_claims(
        self, mock_jwt, mock_pyjwkclient
    ):
        _verified_decode_raises(mock_jwt, jwt.MissingRequiredClaimError("sub"))
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            validate_jwt_token(
                jwt_token="aaaaa.bbbbbb.cccccc",  # noqa: S106
                jwks_url="https://mock_jwks_url",
                issuer="https://mock_issuer",
                audience="app_id_xxxx",
            )
        self.assertEqual(
            str(ctx.exception),
            'Token is missing required claims: Token is missing the "sub" claim',
        )

    def test_validate_jwt_token_jwks_error(self, mock_jwt, mock_pyjwkclient):
        _verified_decode_raises(
            mock_jwt, jwt.exceptions.PyJWKClientError("Unable to find a signing key")
        )
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            validate_jwt_token(
                jwt_token="aaaaa.bbbbbb.cccccc",  # noqa: S106
                jwks_url="https://mock_jwks_url",
                issuer="https://mock_issuer",
                audience="app_id_xxxx",
            )
        self.assertEqual(
            str(ctx.exception),
            "JWKS or key processing error: Unable to find a signing key",
        )

    def test_validate_jwt_token_invalid_token(self, mock_jwt, mock_pyjwkclient):
        _verified_decode_raises(mock_jwt, jwt.InvalidTokenError("Not enough segments"))
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            validate_jwt_token(
                jwt_token="aaaaa.bbbbbb.cccccc",  # noqa: S106
                jwks_url="https://mock_jwks_url",
                issuer="https://mock_issuer",
                audience="app_id_xxxx",
            )
        self.assertEqual(str(ctx.exception), "Invalid token: Not enough segments")
