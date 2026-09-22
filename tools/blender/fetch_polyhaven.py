"""Fetch CC0 Poly Haven HDRIs + PBR texture sets into tools/blender/vendor/.
Provenance recorded in vendor/manifest.json. No API key required.
Usage: python tools/blender/fetch_polyhaven.py
"""
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, 'vendor')
HDRIS = ['spruit_sunrise', 'kloppenheim_06_puresky', 'kiara_9_dusk',
         'qwantani_night_puresky', 'brown_photostudio_02']
TEXTURES = ['bark_brown_01', 'forest_ground_04', 'stone_wall_05', 'marble_01', 'oak_wood_planks']
TEX_MAPS = ['Diffuse', 'nor_gl', 'Rough', 'AO']


UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) StoryworldBot/0.3 (CC0 asset fetch)'}


def get_json(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print(f'retry {url}: {e}')
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f'failed: {url}')


def download(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f'skip (cached): {os.path.basename(dest)}')
        return dest
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, 'wb') as f:
                f.write(r.read())
            if os.path.getsize(dest) > 0:
                print(f'got: {os.path.basename(dest)} ({os.path.getsize(dest) // 1024}KB)')
                return dest
        except Exception as e:
            print(f'retry {os.path.basename(dest)}: {e}')
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f'download failed: {url}')


os.makedirs(os.path.join(VENDOR, 'hdris'), exist_ok=True)
os.makedirs(os.path.join(VENDOR, 'textures'), exist_ok=True)
manifest = {'hdris': {}, 'textures': {}}

for slug in HDRIS:
    files = get_json(f'https://api.polyhaven.com/files/{slug}')
    hdri_key = next((k for k in files if 'hdri' in k.lower()), None)
    assert hdri_key, f'no hdri key in {slug}: {list(files)}'
    entry = files[hdri_key].get('1k') or files[hdri_key].get('2k')
    file_entry = entry.get('hdr') or entry.get('exr') or next(iter(entry.values()))
    ext = '.hdr' if 'hdr' in file_entry['url'] else '.exr'
    dest = os.path.join(VENDOR, 'hdris', slug + ext)
    download(file_entry['url'], dest)
    manifest['hdris'][slug] = {'file': os.path.relpath(dest, HERE), 'url': file_entry['url']}

for slug in TEXTURES:
    files = get_json(f'https://api.polyhaven.com/files/{slug}')
    got = {}
    for m in TEX_MAPS:
        if m in files and '1k' in files[m] and 'jpg' in files[m]['1k']:
            u = files[m]['1k']['jpg']['url']
            dest = os.path.join(VENDOR, 'textures', f'{slug}_{m.lower()}_1k.jpg')
            download(u, dest)
            got[m] = os.path.relpath(dest, HERE)
    manifest['textures'][slug] = got

json.dump(manifest, open(os.path.join(VENDOR, 'manifest.json'), 'w'), indent=2)
total = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(VENDOR) for f in fs)
print(f'vendor total: {total / 1024 / 1024:.1f}MB')
print('manifest written')
