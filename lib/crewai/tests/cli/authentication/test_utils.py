import unittest
from unittest.mock import MagicMock, patch

from crewai.auth.utils import validate_jwt_token
import jwt


def _use_real_jwt_errors(mock_jwt: MagicMock) -> None:
    for name in (
        "ExpiredSignatureError",
        "InvalidAudienceError",
        "InvalidIssuerError",
        "MissingRequiredClaimError",
        "InvalidTokenError",
    ):
        setattr(mock_jwt, name, getattr(jwt, name))
    mock_jwt.exceptions = jwt.exceptions


@patch("crewai_core.auth.utils.PyJWKClient", return_value=MagicMock())
@patch("crewai_core.auth.utils.jwt")
class TestUtils(unittest.TestCase):
    def test_validate_jwt_token(self, mock_jwt, mock_pyjwkclient):
        mock_jwt.decode.return_value = {"exp": 1719859200}

        mock_pyjwkclient.return_value.get_signing_key_from_jwt.return_value = MagicMock(
            key="mock_signing_key"
        )

        jwt_token = "aaaaa.bbbbbb.cccccc"

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

    def _validate(self):
        return validate_jwt_token(
            jwt_token="aaaaa.bbbbbb.cccccc",
            jwks_url="https://mock_jwks_url",
            issuer="https://mock_issuer",
            audience="app_id_xxxx",
        )

    def test_validate_jwt_token_expired(self, mock_jwt, mock_pyjwkclient):
        _use_real_jwt_errors(mock_jwt)
        mock_jwt.decode.side_effect = [{}, jwt.ExpiredSignatureError]
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            self._validate()
        self.assertEqual(str(ctx.exception), "Token has expired.")

    def test_validate_jwt_token_invalid_audience(self, mock_jwt, mock_pyjwkclient):
        _use_real_jwt_errors(mock_jwt)
        mock_jwt.decode.side_effect = [{"aud": "other_app"}, jwt.InvalidAudienceError]
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            self._validate()
        self.assertEqual(
            str(ctx.exception),
            "Invalid token audience. Got: 'other_app'. Expected: 'app_id_xxxx'",
        )

    def test_validate_jwt_token_invalid_issuer(self, mock_jwt, mock_pyjwkclient):
        _use_real_jwt_errors(mock_jwt)
        mock_jwt.decode.side_effect = [{}, jwt.InvalidIssuerError]
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            self._validate()
        self.assertEqual(
            str(ctx.exception),
            "Invalid token issuer. Got: '[no issuer found]'. Expected: 'https://mock_issuer'",
        )

    def test_validate_jwt_token_missing_required_claims(
        self, mock_jwt, mock_pyjwkclient
    ):
        _use_real_jwt_errors(mock_jwt)
        mock_jwt.decode.side_effect = [{}, jwt.MissingRequiredClaimError("sub")]
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            self._validate()
        self.assertEqual(
            str(ctx.exception),
            'Token is missing required claims: Token is missing the "sub" claim',
        )

    def test_validate_jwt_token_jwks_error(self, mock_jwt, mock_pyjwkclient):
        _use_real_jwt_errors(mock_jwt)
        mock_pyjwkclient.return_value = MagicMock()
        mock_pyjwkclient.return_value.get_signing_key_from_jwt.side_effect = (
            jwt.exceptions.PyJWKClientError("Unable to find a signing key")
        )
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            self._validate()
        self.assertEqual(
            str(ctx.exception),
            "JWKS or key processing error: Unable to find a signing key",
        )

    def test_validate_jwt_token_invalid_token(self, mock_jwt, mock_pyjwkclient):
        _use_real_jwt_errors(mock_jwt)
        mock_jwt.decode.side_effect = [{}, jwt.InvalidTokenError("Not enough segments")]
        with self.assertRaises(Exception) as ctx:  # noqa: B017
            self._validate()
        self.assertEqual(str(ctx.exception), "Invalid token: Not enough segments")
