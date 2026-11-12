# BreadGit distribution

BreadGit 0.1.4 is a prerelease with **cryptographically signed in-app updates**. Windows executables remain Authenticode **NotSigned**.

- [Download](https://breadpack.github.io/breadgit-releases/)
- [Release](https://github.com/breadpack/breadgit-releases/releases/tag/v0.1.4-update-signed)
- [Signed update channel](https://breadpack.github.io/breadgit-releases/updates/current.json)
- [Distribution status](https://breadpack.github.io/breadgit-releases/stable/status.json)
- [Actual isolated Windows acceptance](https://breadpack.github.io/breadgit-releases/acceptance/0.1.4.json)

Users of 0.1.1 or earlier must manually install 0.1.4 once. Future updates are checked and downloaded automatically, verified against keys compiled into the app, then installed after review and consent when Git is idle. Closing the update notice dismisses it for that launch. Interrupted health verification triggers rollback; user repositories and settings are preserved.

Windows 11 24H2+ x64, per-user installation. No test certificate installation is required. Windows or organization policy may warn or block unsigned executables. Update signatures do not provide Windows publisher identity or SmartScreen reputation.

The legacy `/manual/latest.json` feed remains notification-only for old clients (`automaticInstall:false`); it carries no installer authority. The separate Windows-code-signed `/stable/current.json` remains absent. The active update-signature-only channel is `/updates/current.json`.

This repository contains binary distribution metadata and notices, not private application source or signing keys. Trust roots are compiled into the application. Signed metadata expires after 30 days and must be renewed by the release owner with a higher catalog sequence. Existing immutable installer assets must not be replaced.
