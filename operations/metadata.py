"""Bounded verification shared by the private worker and keyless public monitor."""
import base64
import hashlib
import json
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

BASE = "https://breadpack.github.io/breadgit-releases/"
PRODUCT = "com.breadgit.desktop"
DAY = 86400


class Failure(Exception):
    pass


def require(condition, code):
    if not condition:
        raise Failure(code)


def parse(raw):
    require(len(raw) <= 1024 * 1024, "METADATA_SIZE")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "DUPLICATE_FIELD")
            result[key] = value
        return result

    return json.loads(raw, object_pairs_hook=unique)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(raw, role, roots, now, allow_expired=False):
    envelope = parse(raw)
    require(set(envelope) == {"schemaVersion", "keyId", "payload", "signature"}, "ENVELOPE_SCHEMA")
    require(envelope["schemaVersion"] == 1, "ENVELOPE_SCHEMA")
    keys = [k for k in roots if k["role"] == role and k["keyId"] == envelope["keyId"]]
    require(len(keys) == 1, "UNTRUSTED_KEY")
    key = keys[0]
    require(key["notBefore"] <= now < key["notAfter"], "KEY_EXPIRED")
    payload = base64.b64decode(envelope["payload"], validate=True)
    signature = base64.b64decode(envelope["signature"], validate=True)
    try:
        Ed25519PublicKey.from_public_bytes(base64.b64decode(key["publicKey"], validate=True)).verify(
            signature, f"BreadGit/{role}/v1\0".encode() + payload
        )
    except Exception:
        raise Failure("BAD_SIGNATURE") from None
    value = parse(payload)
    require(value["schemaVersion"] == 1 and value["productId"] == PRODUCT, "WRONG_PRODUCT")
    require(value["issuedAt"] <= now + 300, "FUTURE_METADATA")
    require(0 < value["expiresAt"] - value["issuedAt"] <= 31 * DAY, "INVALID_LIFETIME")
    require(allow_expired or value["expiresAt"] > now, "METADATA_EXPIRED")
    return value


def semantic_release(value):
    return {k: v for k, v in value.items() if k not in ("issuedAt", "expiresAt")}


def semantic_catalog(value):
    result = {k: v for k, v in value.items() if k not in ("issuedAt", "expiresAt", "sequence")}
    for name in ("stable", "pilot"):
        if result.get(name):
            result[name] = {k: v for k, v in result[name].items() if k not in ("manifestUrl", "manifestSha256")}
    return result


def fetch(url):
    require(url.startswith(BASE + "updates/") and not urlsplit(url).query, "UNAPPROVED_URL")
    with urlopen(Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "BreadGit-metadata-monitor/1"}), timeout=30) as response:
        require(response.url.startswith(BASE + "updates/"), "UNAPPROVED_REDIRECT")
        return response.read(1024 * 1024 + 1)


def public_state(roots, now, minimum_sequence=1):
    pointer = parse(fetch(BASE + "updates/current.json"))
    raw = fetch(pointer["catalogUrl"])
    require(digest(raw) == pointer["catalogSha256"], "CATALOG_DIGEST")
    catalog = verify(raw, "catalog", roots, now)
    require(catalog["sequence"] == pointer["sequence"] >= minimum_sequence, "REPLAY")
    releases = {}
    for name in ("stable", "pilot"):
        slot = catalog.get(name)
        if slot:
            raw = fetch(slot["manifestUrl"])
            require(digest(raw) == slot["manifestSha256"], "RELEASE_DIGEST")
            release = verify(raw, "release", roots, now)
            require(release["releaseId"] == slot["releaseId"] and release["version"] == slot["version"], "RELEASE_IDENTITY")
            releases[release["version"]] = release
    return pointer, catalog, releases
