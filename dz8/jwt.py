import base64
import json
import hmac
import hashlib
from datetime import datetime, timezone


class InvalidTokenError(Exception):
    pass


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode())


def encode(payload: dict, key: str, algorithm: str = "HS256") -> str:
    if algorithm != "HS256":
        raise InvalidTokenError("Unsupported algorithm")

    header = {"typ": "JWT", "alg": algorithm}
    payload = payload.copy()
    exp = payload.get("exp")
    if isinstance(exp, datetime):
        payload["exp"] = int(exp.timestamp())

    header_part = _b64encode(json.dumps(header, separators=(",", ":")).encode())
    payload_part = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_part}.{payload_part}".encode()
    signature = hmac.new(key.encode(), signing_input, hashlib.sha256).digest()
    return f"{header_part}.{payload_part}.{_b64encode(signature)}"


def decode(token: str, key: str, algorithms: list[str] | None = None) -> dict:
    if algorithms and "HS256" not in algorithms:
        raise InvalidTokenError("Unsupported algorithm")

    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as e:
        raise InvalidTokenError("Malformed token") from e

    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_sig = hmac.new(key.encode(), signing_input, hashlib.sha256).digest()
    actual_sig = _b64decode(signature_b64)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise InvalidTokenError("Bad signature")

    payload = json.loads(_b64decode(payload_b64).decode())
    exp = payload.get("exp")
    if exp is not None and int(exp) < int(datetime.now(timezone.utc).timestamp()):
        raise InvalidTokenError("Token expired")
    return payload
