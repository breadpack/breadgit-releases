"""Public, credential-free watchdog; exits nonzero on renewal or freshness failure."""
import argparse
import time
from pathlib import Path
from metadata import BASE, DAY, Failure, fetch, parse, public_state, require, verify


def check(roots, now, status, catalog, releases):
    require(status["status"] == "ok", "RENEWAL_FAILED")
    require(-300 <= now - status["lastVerifiedAt"] <= 30 * 3600, "RENEWAL_HEARTBEAT_STALE")
    require(status["sequence"] == catalog["sequence"], "RENEWAL_NOT_CONFIRMED")
    require(catalog["expiresAt"] - now > 14 * DAY, "CATALOG_EXPIRY_NEAR")
    require(all(r["expiresAt"] - now > 14 * DAY for r in releases.values()), "RELEASE_EXPIRY_NEAR")
    require(all(k["notAfter"] - now > 31 * DAY for k in roots if k["role"] in ("catalog", "release")), "SIGNING_KEY_EXPIRY_NEAR")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, required=True)
    args = parser.parse_args()
    roots = parse(args.roots.read_bytes())
    now = int(time.time())
    _, catalog, releases = public_state(roots, now)
    # The discovery index must cover rollback sources too, not just the target.
    status = parse(fetch(BASE + "updates/renewal-status.json"))
    for version in status["supportedVersions"]:
        require(version.count(".") == 2 and all(p.isdigit() for p in version.split(".")), "INVALID_VERSION")
        discovery = parse(fetch(BASE + "updates/discovery/" + version))
        link = discovery["assets"]["links"][0]
        require(link["name"] == "release.signed.json", "DISCOVERY_SCHEMA")
        release = verify(fetch(link["url"]), "release", roots, now)
        require(release["version"] == version, "DISCOVERY_IDENTITY")
        releases[version] = release
    check(roots, now, status, catalog, releases)
    print(f"METADATA_HEALTHY sequence={catalog['sequence']} supported={len(releases)} remainingDays={(catalog['expiresAt']-now)//DAY}")


if __name__ == "__main__":
    try:
        main()
    except Failure as error:
        print("METADATA_MONITOR_FAILED code=" + str(error))
        raise SystemExit(1)
    except Exception:
        print("METADATA_MONITOR_FAILED code=FETCH_OR_SCHEMA_ERROR")
        raise SystemExit(1)
