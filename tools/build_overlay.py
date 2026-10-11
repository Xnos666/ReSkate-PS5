#!/usr/bin/env python3
"""Stage the source snapshot against an existing prepared WoWPS5 dependency tree.

This is an advanced Linux build helper, not a fresh-machine bootstrapper.
It never deploys files to a console or edits the supplied dependency tree.
"""
import argparse
from pathlib import Path
import shutil
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', type=Path, required=True, help='Extracted ReSkate-PS5-source')
p.add_argument('--base', type=Path, required=True, help='Prepared WoWPS5 checkout with build/{radv,ps5-wine,ps5-tls}')
p.add_argument('--output', type=Path, required=True, help='New, empty output directory')
p.add_argument('--configure-only', action='store_true')
a = p.parse_args()
source, base, output = (x.resolve() for x in (a.source, a.base, a.output))
if output.exists():
    raise SystemExit('Output must not already exist')
for rel in ('build/radv/lib/libvulkan_radeon.ps5.a', 'build/ps5-wine/wine-unix.o', 'app/.deps/native/ps5-payload-sdk/toolchain/prospero.cmake'):
    if not (base / rel).is_file():
        raise SystemExit('Prepared dependency missing: ' + rel)
if not (source / 'WoWPS5/app/ps5/CMakeLists.txt').is_file():
    raise SystemExit('Incorrect source archive root')
output.mkdir(parents=True)
for name in ('app', 'runtime'):
    shutil.copytree(source / 'WoWPS5' / name, output / name)
shutil.copytree(source / 'glm', output / 'app/external/glm', dirs_exist_ok=True)
(output / 'build').mkdir()
for name in ('radv', 'ps5-wine', 'ps5-tls'):
    (output / 'build' / name).symlink_to(base / 'build' / name, target_is_directory=True)
link = output / 'app/ps5/tools/link-title.sh'
text = link.read_text()
text = text.replace('/opt/wowps5-perf/WoWPS5/app/dist/PPSA99220', str(base / 'app/dist/PPSA99220'))
link.write_text(text)
sdk = base / 'app/.deps/native/ps5-payload-sdk'
vulkan = base / 'vendor/PS5_Vulkan'
subprocess.run(['cmake', '-S', str(output / 'app/ps5'), '-B', str(output / 'app/build/ps5'), '-G', 'Ninja',
                '-DCMAKE_TOOLCHAIN_FILE=' + str(sdk / 'toolchain/prospero.cmake'),
                '-DPS5_VULKAN_DIR=' + str(vulkan), '-DCMAKE_BUILD_TYPE=Release'], check=True)
if not a.configure_only:
    subprocess.run(['ninja', '-C', str(output / 'app/build/ps5'), 'title'], check=True)
print('Overlay ready. Review and regenerate release notices before distributing a rebuilt title.')
