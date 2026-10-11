# Pre-publication review

An independent Security Review examined the initial repository changes, installer, workflows, website, diagnostic sources, and the ignored binary overlay. It reported one P2 issue: the runtime ownership marker was incorrectly used to authorize the title directory as well.

The installer now checks a separate marker in each existing destination, validates both before writing, and includes a regression test for a recognized runtime alongside an unrelated title. The post-fix automated tests cover this case. The independent review was not rerun after the fix.

The review verified the initial overlay's 49 file hashes and reported no other actionable findings in its scope. The corresponding-source archive was still being exported and was excluded from that review. Source provenance/privacy inventory and release checksum checks are separate publishing checks, not a second security review or a guarantee of safety.

Installer validation used dry-run mode and made no installation writes to the console. The existing prototype's crash logs were separately captured for diagnosis. Hardware stability and gameplay remain unresolved; see STATUS.md.

## October 11, 2026 documentation update

An independent Security Review examined the eight changed documentation, website, issue-template, and publication-check files, including the Wine/vkd3d-proton clarification. It found no actionable issues in that scope. Development measurements are distinguished from the unchanged downloadable preview, and no credentials, private console addresses, personal paths, or memory-range tables were exposed.

The reviewer did not independently reproduce the hardware measurements or re-review binaries/runtime sources. Nine installer tests and the publication validator passed locally; desktop and mobile layout/image checks also passed. This review does not qualify the newer private runtime for release.
