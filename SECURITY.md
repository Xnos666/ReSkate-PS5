# Security

The installer is intended for a trusted LAN and a console you control. FTP is unencrypted. It uses anonymous login and the PS5 `SELF` command, writes only under the two ReSkate directories, hashes inputs, and reads uploaded files back before promotion. Checksums detect corruption; they do not authenticate a malicious replacement of both code and its manifests. Obtain the repository and bundle from the project's release together.

The installer does not edit global app databases, install a jailbreak, alter firmware, disable antivirus, or post logs. It requires the application to be closed. Existing installations without its marker are rejected. Console services and filesystem integrity are trusted; this is not a sandbox against a compromised console or hostile LAN peer.

Please report suspected vulnerabilities through GitHub's private vulnerability reporting if enabled. Otherwise open an issue describing the affected component without secrets or an exploit containing personal information. Do not upload prefixes, databases, account tokens, game files, or raw logs.
