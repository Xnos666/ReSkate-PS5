# Test ledger

Status for the first experimental publication. Evidence comes from one local PS5 setup and diagnostic logs; no second-console replication is claimed.

## Observed passes

- Native title launch and Windows loader probe: file and thread operations worked.
- Direct3D 12 diagnostic: device creation, DXGI clear/present, and GPU fence completion passed.
- Frame-latency waitable-object diagnostic passed.
- Cross-queue future waits and direct/copy/compute signaling passed with both default queues and `single_queue`.
- XInput controller 0 was detected in the probe. This is not evidence that in-game controls work.
- The game and integration files passed a 155-file console SHA-256 check during the prototype installation.
- The ReSkate runtime initialized, the loading screen appeared, and the user observed shader compilation.
- vkd3d-proton and RADV caches grew. The native RADV cache reached roughly 48 MiB in one snapshot; this is not a target size or a completion signal.
- The user confirmed the official blue RE icon on the home screen.

## Failed or incomplete

- An early copy coincided with a console crash and reboot.
- Early launches failed before visible loading; native `d3dcompiler_47.dll` and the matching offline initialization flag resolved those particular blockers.
- Subsequent runs stalled or closed during shader/loading work.
- Several diagnostic launches had explicit time limits (including 180 and 420 seconds). Their exit code 124 was the test deadline, not proof of a spontaneous GPU crash.
- A later normal launch had no timeout and continued producing shader-cache activity beyond an hour. The user subsequently clarified that it passed shaders, then crashed with CE-108255-1. Captured logs reached `Local player joined`, `Level active`, and level content loaded. These messages do not prove visible or controllable gameplay. The root cause is unresolved.
- No controllable skater or stable gameplay has been demonstrated. There are no verified gameplay FPS figures.
- A clean installation using the new portable installer on another console remains unverified.
- A fresh-machine rebuild of all native dependencies remains unverified.

## Default configuration

The title requests a 1280 × 720 window and offline initialization. `VKD3D_CONFIG=` selects default queue behavior; the inherited `single_queue` setting is not forced. `WOWPS5_DEADLINE=0` disables the diagnostic timer. Native shader caching remains enabled; compiler optimization has not been disabled.

During testing, manually edited game settings selected low quality and a 30 FPS target. Those user-derived settings blobs are **not** included in the release. The public configuration requests 720p, but it cannot promise every in-game quality option is low on a new prefix.

## Next evidence needed

1. A fresh installation with the published inputs and installer.
2. A bounded reproducer for the shader/loading failure, with native driver stack information.
3. A recording of reaching a controllable skater, accompanied by the exact game, title, firmware, and runtime versions.
4. A sustained gameplay session, followed by separate checks of audio, controls, save/load, and clean exit.
5. Only afterward: broader hardware/firmware compatibility and multiplayer investigation.
