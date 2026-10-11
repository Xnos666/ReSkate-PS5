# Credits and component licenses

- **Dingo-Shenanigans / ReSkate** — launcher, runtime, and official artwork. [Source](https://github.com/Dingo-Shenanigans/ReSkate/tree/d1e6afc951b8fad0e800c7a655c3041d93e143ec), GPL-3.0 repository. Icon: `assets/launcher/icon.ico`; background: `assets/launcher/background.jpg`; splash: `assets/startup_splash.jpg`. PS5 art was resized/padded and encoded as BC7 DDS. Website images are the upstream artwork. They are not screenshots of successful PS5 gameplay.
- **BeLikeBrett / WoWPS5** — single-process Wine title integration and build foundation. [Source](https://github.com/BeLikeBrett/WoWPS5), base revision `c96a9777dd4c6a0c09bdcc125cfc0a678f730988`. New ReSkate changes are supplied with this release.
- **Wine contributors** — LGPL-2.1-or-later. Base `455e3509b98a6919fd4ad1def4803e08c41c03b2`, with the PS5 port and ReSkate bootstrap modifications in the corresponding-source archive.
- **Mihawk / PS5_Vulkan** — GPL-3.0-or-later, revision `4271e2e309d9a7eea3a893f5b94427bb78e586ed`. [Source](https://github.com/mihawk-99/PS5_Vulkan).
- **Mesa contributors / Mihawk's PS5_Mesa** — MIT and per-file licenses, revision `15a5e9933e14f6493a7853e8cf1df973dd093eeb`, with WoWPS5's video-out patch. [Source](https://github.com/mihawk-99/PS5_Mesa).
- **PS5 payload SDK contributors and Mihawk's fork** — GPL-3.0-or-later plus component notices. Title SDK `adc8dd795ada7bf696cd98748aae463a3970ffbb`; RADV build SDK `95c08f27386fc698f6bbe21dde3030140a41d10b`. [Source](https://github.com/mihawk-99/PS5_PayloadSDK).
- **vkd3d-proton contributors** — LGPL-2.1; Windows translation DLLs are taken from the separately supplied pinned base bundle. [Source](https://github.com/HansKristian-Work/vkd3d-proton).
- **LLVM, GnuTLS, Nettle, GMP, Sascha Willems, Dear ImGui, GLM, KTX, tinygltf, volk, Vulkan headers, and their contributors** — retained component licenses and source notices accompany the title/source archives.

The native linked title is GPL-3.0-or-later as a whole. Original component notices remain applicable; the repository's root GPL text does not relicense every third-party file. The new Python installer is MIT, and Wine modifications retain LGPL-2.1-or-later. The minidump shim only forwards to Wine's `dbghelp.MiniDumpWriteDump`.

The bundle deliberately excludes Microsoft's `d3dcompiler_47.dll`, EA game binaries/data, and user-generated caches. Users supply their own compatible local files. No affiliation or endorsement by the upstream ReSkate team, EA, Full Circle, or Sony is implied.
