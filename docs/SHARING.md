# Ready-to-edit sharing drafts

Updated October 11, 2026. These drafts distinguish development progress from the older download. No social posts are sent automatically.

## X

ReSkate PS5 update: skating + Bluetooth DualSense work in a development build. Smoother now, but still ~30 FPS. The download is an older experimental build; these fixes aren't packaged yet. Progress + limitations:
https://wwwshelton19-spec.github.io/ReSkate-PS5/

## Reddit

**Title:** ReSkate PS5 development update — controllable skating and DualSense working, around 30 FPS

The latest development build reaches the city with controllable skating, Bluetooth DualSense input, and a display-filling image on one jailbroken PS5. The app uses the official ReSkate artwork and runs the Windows game through Wine, vkd3d-proton, and RADV.

Recurring local-profile refresh stalls fell from about 95 ms to 2.7 ms, and skating feels smoother. Actual rendering is still around 30 FPS. The approximately 60-per-second simulation update counter is not 60 FPS. Unlimited framerate did not improve it. City loading still takes about 210 seconds in these tests, and stability across maps and long sessions is unresolved.

**The public v0.1.0-experimental download is still the older loading/crash preview.** The latest changes aren't packaged yet: the current memory guards rely on console-specific ranges and need a portable implementation. This is a progress report, not a new gameplay-ready release.

No game files or personal caches are distributed. Fresh-console installation, broad compatibility, and multiplayer remain unverified. Rendering/synchronization diagnostics and work toward portable memory handling would be especially useful.

Website: https://wwwshelton19-spec.github.io/ReSkate-PS5/

Repository: https://github.com/wwwshelton19-spec/ReSkate-PS5
