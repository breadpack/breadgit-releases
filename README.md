# BreadGit distribution

BreadGit 0.1.1 is an **unsigned manual-install prerelease** with in-app new-version notifications. Automatic download/installation and the signed stable channel remain disabled.

- Download: https://breadpack.github.io/breadgit-releases/
- Prerelease: https://github.com/breadpack/breadgit-releases/releases/tag/v0.1.1-manual-unsigned
- Notification-only version feed: https://breadpack.github.io/breadgit-releases/manual/latest.json
- Signed stable status: https://breadpack.github.io/breadgit-releases/stable/status.json

0.1.0 users must manually install 0.1.1 once to receive future notifications. Dismissed notifications return on the next app launch while a newer release remains available. Notifications open only the fixed download homepage; the app does not download or run the unsigned installer.

Windows 11 24H2+ x64, per-user installation. No test certificate installation is required. Windows or organization policy may warn or block this unsigned installer.

This repository contains binary distribution metadata and public notices, not private application source or signing keys. The notification feed is not signed installer authorization. Runtime/installer trust roots are compiled into the application; they are not fetched from this site.
