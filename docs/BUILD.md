# Source and build notes

The experimental binary was built in a prepared Linux/WSL environment. **A complete fresh-machine rebuild has not been verified.** These notes distinguish the exact source handoff from the remaining toolchain setup work; do not treat an untested build recipe as a one-command guarantee.

## Source archive

Download `ReSkate-PS5-corresponding-source.tar.gz` from the same release as the binary. It contains the modified title/runtime sources, the full modified Wine source, pinned PS5 Vulkan/Mesa/SDK sources, GLM, TLS source, and original integration/build scripts. Per-file copyrights and licenses are preserved. The accompanying source inventory records base revisions. The repository contains the portable installer, manifests, configuration, selected diagnostic sources, documentation, and website.

The separate `RADV-driver-SDK-source.tar.gz` contains the exact SDK revision used while building the driver. `ReSkate-PS5-source-links.tar.gz` preserves the upstream relative header/source aliases that were omitted by the regular-file export. Extract that small archive in the same directory **after** the main source archive. These links remain inside their respective source components. The alias inventory is also in `manifests/source-links.json`.

```sh
tar -xzf ReSkate-PS5-corresponding-source.tar.gz
tar -xzf ReSkate-PS5-source-links.tar.gz
```

`SHA256SUMS.txt` covers the bundle and all three source archives. Duplicate source members are removed and personal development-path strings are replaced by generic example paths in the published archive.

`integration-original/` records the build procedure used for the tested binary. Its `/opt/...` paths identify the original build layout; adapt those roots for a different machine. No deployment command is needed to study or build the code. Avoid running inherited console-deployment scripts without reviewing their targets.

## Native dependency chain

1. Set up the pinned PS5 payload SDK and PS5_Vulkan host tools. The inherited `WoWPS5/tools/bootstrap.py` and `dependencies.json` describe the host dependencies. LLVM, mingw-w64, Python, CMake, Ninja, Meson, and Wine host tools are required.
2. Build the RADV release archive from PS5_Mesa with `WoWPS5/runtime/radv-ps5/videoout-mailbox.patch`. The tested archive used assertions off and retained shader caching. Recorded SHA-256: `b09fb0d8e2996effcd2a4288cca2151880c6c04f639f840fcb2a5178cfd306f5`.
3. Build the PS5 TLS libraries (GMP 6.3.0, Nettle 3.10.2, GnuTLS 3.8.13) and Wine's native aggregate using the included Wine PS5 scripts. Those scripts require prepared Wine configure outputs; inspect their prerequisites before running. `build-console.sh --no-deploy` avoids its deployment step.
4. Configure the modified title with CMake's `prospero.cmake` toolchain and the pinned `PS5_VULKAN_DIR`, then build the `title` target. The source snapshot includes the final ReSkate metadata and artwork inputs.
5. Configure Wine for x86_64 Windows modules using mingw and the matching Wine host tools. Build `kernel32.dll`, `sensapi.dll`, `sspicli.dll`, `version.dll`, `wer.dll`, and `wtsapi32.dll` as listed in `integration-original/build.sh`.
6. Build the small minidump forwarding DLL from `minidump-shim.def` with an x86_64 Windows linker. This replaces a missing API-set forwarder; it does not include Microsoft implementation code.

The prototype reused already-built native Wine, RADV, and TLS objects. The new `tools/build_overlay.py` can stage the modified title against an existing prepared WoWPS5 dependency tree without changing that tree. It does not claim to bootstrap all dependencies from a clean OS.

## Bootstrap behavior

The Wine `BaseThreadInitThunk` hook checks `RESKATE_PS5_BOOTSTRAP=1`, confirms it is entering the main PE entrypoint, and initializes `C:\Games\ReSkate\ReSkate.dll` once before `Skate.exe`. Initialization happens outside Wine's loader lock. The game executable is unmodified.

The native title supplies the matching global-offline flag, Steam app ID `3354750`, a 720p window request, and disabled Discord/crash-reporting hooks. Diagnostic output goes to `/data/reskate/runtime.log`. The Windows username in the clean seed remains `wowps5`; the prefix is isolated under `/data/reskate`.

## Validate an installer change

```text
python -m unittest discover -s tests -v
python -m compileall -q install.py tools tests
```

Then perform a dry run with the exact documented local inputs. A dry run does not prove a fresh-console installation. Hardware tests must record their firmware, title hash, game/runtime versions, and observed outcome. Do not mark gameplay supported solely because D3D12 probes or a loading screen work.
