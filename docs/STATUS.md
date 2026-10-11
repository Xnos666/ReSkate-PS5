# Development status and test ledger

Updated **October 11, 2026**. These observations come from one PS5 setup, user feedback, and local diagnostic logs. No second-console replication is claimed.

## Development build versus the download

The newer development build reaches **controllable skating** with a **Bluetooth DualSense** and a **display-filling image**. The user confirmed smoother motion after reducing recurring stalls. Actual gameplay rendering remains **about 30 FPS**; reliable 60 FPS has not been achieved.

**The downloadable `v0.1.0-experimental` bundle is unchanged.** It is the earlier loading/crash preview and does not contain the newer input/display changes or memory-read guards. Updating this documentation does not update installed binaries. The current private guards rely on observed native execute-only memory ranges specific to the tested console/runtime and are not suitable for a portable release yet. Do not copy address tables from another console.

## Latest measured results

- **Gameplay and input:** the user reached the city, controlled the skater, and confirmed Bluetooth DualSense input. The PS button alone was not treated as proof of game input.
- **Display:** a 3840 × 2160 game surface filled the display. A 1920 × 1080 game-surface trial produced a small image surrounded by black, even with DXGI stretch selected. The console output had been changed to 1080p by the user; output mode and game-surface size are different. A full-size surface does not prove native 4K internal rendering.
- **Stalls:** recurring local-profile refresh work fell from approximately 94–95 ms to 2.66–2.73 ms after guarded fast memory reads. The user described the result as definitely smoother. This does not mean the whole game became 35 times faster.
- **Simulation versus rendering:** client updates reached about 60 per second, while presented gameplay frames remained around 29.6–30 FPS. Simulation frequency is not rendering FPS.
- **Frame-target comparison:** the supported Unlimited option produced about 30 FPS, with no meaningful improvement over the 60 FPS target. Turning the diagnostic HUD off also left approximately 30 presentation calls per second. The 60 FPS target and prior graphics DLL were restored afterward.
- **Presentation timing:** in the Unlimited trial, the DXGI Present call averaged approximately 0.021–0.024 ms. Most frame time was outside that call; GPU waits elsewhere and game scheduling still need investigation. This does not identify a particular limiter.
- **Simple graphics test:** a standalone solid-color D3D12 workload completed 90 timed synchronized frames in 1.5015 seconds, approximately 59.94 per second, after warm-up. That demonstrates 60 Hz presentation for a trivial workload, not 60 FPS gameplay. Unsynchronized submission counts are not displayed FPS.
- **Loading:** repeated city loads took approximately 210 seconds, around 204–206 seconds in “Starting level load.” One PC comparison reached city content in 5.26 seconds. This is not a controlled GPU benchmark, and the long PS5 stage is not established to be shader compilation alone.

## Changes and unsuccessful experiments

The development work includes controller-state handling, a full-size game surface, guarded fast memory reads, and a self-process memory-read guard against observed native execute-only ranges. Host and console guard self-tests passed in the tested environment. First-chance exception file logging was disabled during performance trials; that change alone did not resolve the native fault.

FSR Performance felt about the same or worse to the tester. Reducing the game surface to 1080p caused the small-image regression. A reported-VRAM limit kept the stock mesh pool, but its combined trial with engine/readiness settings did not establish faster usable loading. A readiness bypass returned through the loading flow and was not retained. The smoother configuration was restored.

An earlier map transition failed a roughly 2 GiB GPU allocation. Native memory faults and the earlier CE-108255-1 application error were also observed during development. These failures are not all assigned one cause. No long-session or arbitrary-map stability claim is made.

## Earlier release validation

The original diagnostic probes passed Windows file/thread operations, D3D12 device creation, clear/present, GPU fences, frame-latency waitable objects, and cross-queue synchronization. Controller 0 detection in that diagnostic was separate from the later in-game input confirmation. The official blue RE home-screen artwork was confirmed.

The portable installer passed nine automated tests, including the destination-ownership regression found in the initial security review. A full local dry run validated 2,204 selected files (13.77 GiB), before a license text was added. This was not a clean installation on a second console. Original source/release validation is documented in [REVIEW.md](REVIEW.md).

The **published release** requests a 1280 × 720 window, default queue behavior, offline initialization, and no forced deadline. User-derived game settings, saves, caches, and the development address maps are not supplied. The newer full-screen/performance results must not be assumed for those original defaults.

## Remaining work

1. Replace console-specific memory-range assumptions with a portable, validated approach and package matching source changes.
2. Investigate game rendering, GPU waits, and synchronization to explain the remaining approximately 30 FPS behavior.
3. Diagnose the long level-readiness stage and map-transition memory failure.
4. Verify clean installation on another console and a complete build from a fresh toolchain.
5. Test sustained gameplay, save/load, audio, clean exit, and broader firmware/model compatibility. Multiplayer remains untested.

No gameplay-ready or 60 FPS binary release is announced by this update.
