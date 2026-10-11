"""Validate tracked publication structure without private game inputs."""
from pathlib import Path
from html.parser import HTMLParser
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import install
root = Path(__file__).resolve().parents[1]
for name in ('game.json', 'cache.json', 'runtime.json', 'bundle.json'):
    rows = install.manifest(name)
    if not rows:
        raise ValueError('Empty input manifest: ' + name)
class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src') and value and not value.startswith(('https:', '#')):
                target = (root / 'site' / value).resolve()
                if not target.is_relative_to(root / 'site') or not target.is_file():
                    raise ValueError('Missing or unsafe site asset: ' + value)
Links().feed((root / 'site/index.html').read_text(encoding='utf-8'))
text = (root / 'site/index.html').read_text(encoding='utf-8').lower()
if not all(phrase in text for phrase in ('around 30 fps', 'older loading/crash preview', 'not included', 'crashes remain')):
    raise ValueError('Site must disclose the current experimental status')
print('Manifest structure, local site links, and status disclosure: PASS')
