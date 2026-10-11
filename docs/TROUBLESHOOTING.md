# Troubleshooting

## Shader count moves slowly or stops

First-launch compilation can be expensive, but waiting longer is not a proven fix for this build. The untimed test eventually failed. Record whether the number is changing and the elapsed time; distinguish a stationary loading animation from an application exit or console reboot.

Preserve these PS5-generated caches across runs:

```text
/data/reskate/prefix/dosdevices/c:/Games/ReSkate/vkd3d-proton.cache
/data/homebrew/PPSA99223/radv-shader-cache/
```

The vkd3d cache may also have a `.write` companion. Do not replace these with another PC's GPU cache. Do not delete caches as a routine speed-up: deleting them discards previous compilation work. The separate ReSkate content cache under the prefix is required game content, not a shader cache.

The RADV build already uses a release configuration. Disabling compiler optimization has not been qualified and is not an advertised speed fix. See [Mesa's environment-variable documentation](https://docs.mesa3d.org/envvars.html) for upstream diagnostic options; changes can affect compatibility and performance.

## Game closes after an exact interval

Check `/data/reskate/launch.txt` and any one-shot `/data/homebrew/PPSA99223/wine-run.txt`. `WOWPS5_DEADLINE=0` is the normal no-timeout setting. A positive deadline was used in earlier diagnostics and can intentionally terminate a test. Do not confuse that with the untimed failure, which remains unresolved.

## Immediate exit

Verify the matching game, ReSkate runtime, native compiler DLL, and content cache. The bootstrap's exit codes are 120 (ReSkate DLL failed to load), 121 (initialization export missing), and 122 (initialization returned failure). Do not mix arbitrary versions to bypass validation.

## Wrong title or picture

The correct title is `PPSA99223`, with `sce_sys/param.json`, `icon0.png`, `pic0.dds`, and `pic1.dds` from this release. Move away from the tile and back. If necessary, use your homebrew manager's supported remove/re-register flow after closing the app. **Do not edit global PS5 app databases.** The earlier console-specific database repair is not part of the public package.

## FTP disconnects

Stop if the console reboots. Reactivate the jailbreak and services, return to the home screen, then rerun the installer. Use a stable LAN. The installer verifies full files after transfer and does not resume an unchecked partial prefix. Do not launch while copying.

## Reporting a failure

Record firmware, homebrew manager/enabler versions, game build, release tag, elapsed time, visible shader count, and whether the app closed or the entire console rebooted. Relevant local logs are `/data/reskate/runtime.log` (replaced on each launch) and `C:/Games/ReSkate/logs/ReSkate.log` inside the Wine prefix (may contain multiple sessions).

Read and redact logs before sharing: remove LAN addresses, usernames, local paths, account identifiers, lobby codes, and tokens. Share a short relevant excerpt, not your entire prefix or console databases. Game data and content caches must stay local.

## CE-108255-1 after shaders

The latest user test passed shader compilation and then showed CE-108255-1. The captured game log reached `Local player joined`, `Level active`, and `Level content loaded` before ending. No controllable skating session was confirmed. The runtime log does not establish a root cause.

[Sony describes CE-108255-1](https://www.playstation.com/en-ie/support/error-codes/ps5/ce-108255-1/) as a game/application error. This general code cannot by itself distinguish a game bug, Wine problem, native driver fault, or another failure. Preserve the caches and record the last visible screen and short sanitized log excerpts for diagnosis.
