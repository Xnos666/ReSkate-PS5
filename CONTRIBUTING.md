# Contributing

Start with the status ledger. This is an experimental loader, and the immediate goal is diagnosing the failure between shader compilation and gameplay.

Include the exact release, game build, firmware, enabler, and observed result in test reports. Separate device/probe success from actual gameplay. Keep personal data and game-derived assets out of commits and issues.

Installer changes should preserve strict input checks, confined paths, readback verification, and a network-free dry run. Run the unit tests. Changes to native code need a source/provenance update and a hardware test when possible. Do not claim a performance improvement from one cache-warm launch without a controlled comparison.
