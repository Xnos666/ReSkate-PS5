# Pre-publication review

An independent Security Review examined the initial repository changes, installer, workflows, website, diagnostic sources, and the ignored binary overlay. It reported one P2 issue: the runtime ownership marker was incorrectly used to authorize the title directory as well.

The installer now checks a separate marker in each existing destination, validates both before writing, and includes a regression test for a recognized runtime alongside an unrelated title. The post-fix automated tests cover this case. The independent review was not rerun after the fix.

The review verified the initial overlay's 49 file hashes and reported no other actionable findings in its scope. The corresponding-source archive was still being exported and was excluded from that review. Source provenance/privacy inventory and release checksum checks are separate publishing checks, not a second security review or a guarantee of safety.

No console writes were made during publication validation. Hardware stability and gameplay remain unresolved; see STATUS.md.
