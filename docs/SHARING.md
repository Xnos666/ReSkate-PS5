# Ready-to-edit sharing drafts

These drafts describe the actual experimental status. No social posts are sent automatically.

## X

ReSkate PS5 experimental launcher is public: Wine + vkd3d-proton + RADV, with the official RE artwork. It reaches loading/shader compilation; gameplay is NOT verified and crashes remain. Bring your own game. Testers welcome:
https://wwwshelton19-spec.github.io/ReSkate-PS5/

## Reddit

**Title:** ReSkate PS5 experimental launcher — loading/shader compilation reached, gameplay still unverified

I've published the ReSkate PS5 integration, a detailed setup guide, verified-input installer, and source/build notes. It builds on WoWPS5's Wine + vkd3d-proton + RADV approach and uses its own home-screen title with the official blue RE icon.

Current status: the game reaches loading and compiles shaders, and the D3D12/queue/controller-detection probes pass. It still stalls or exits, and the latest test passed shaders and then crashed with CE-108255-1. There is no verified controllable gameplay, FPS claim, or multiplayer support yet.

The release includes no game data or personal caches. You need your own exact compatible PC game/runtime/cache and a jailbroken PS5. A fresh install on a second console is still needed. Feedback on shader compilation and native driver diagnostics would be especially useful.

Website: https://wwwshelton19-spec.github.io/ReSkate-PS5/

Repository: https://github.com/wwwshelton19-spec/ReSkate-PS5
