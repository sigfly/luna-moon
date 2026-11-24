"""Build a single-file offline atlas from NASA TIFFs using GDAL.

Run from any directory: python tools/build.py. Requirements: GDAL CLI, Python
3.10+. Source TIFFs are cached locally and never committed.
"""
from pathlib import Path
import base64
import gzip
import subprocess
import urllib.request
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache'
ASSETS = ROOT / 'assets'
BASE = 'https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/'


def download(name, filename):
    path = CACHE / filename
    if not path.exists():
        temporary = path.with_suffix('.part')
        urllib.request.urlretrieve(BASE + name, temporary)
        temporary.replace(path)
    return path


def run(*args):
    subprocess.run([str(x) for x in args], check=True)


def embed(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def main():
    CACHE.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    color = ASSETS / 'lroc-16k.jpg'
    height = ASSETS / 'lola-8k.delta16.gz'
    if not color.exists():
        src = download('lroc_color_16bit_srgb_16k.tif', 'color.tif')
        run('gdal_translate', '-of', 'JPEG', '-ot', 'Byte', '-scale', '0', '65535', '0', '255', '-co', 'QUALITY=92', '-co', 'WORLDFILE=NO', src, color)
    if not height.exists():
        src = download('ldem_64_uint.tif', 'height.tif')
        raw = CACHE / 'height.raw'
        run('gdal_translate', '-of', 'ENVI', '-ot', 'UInt16', '-outsize', '8192', '4096', '-r', 'average', src, raw)
        assert raw.stat().st_size == 8192 * 4096 * 2
        header = raw.with_suffix('.hdr').read_text()
        assert 'byte order = 0' in header, header
        # Row-wise modulo-65536 differences preserve every sample losslessly
        # while making neighboring heights more compressible.
        with raw.open('rb') as inp, gzip.open(height, 'wb', compresslevel=6) as out:
            for _ in range(4096):
                row = np.frombuffer(inp.read(8192 * 2), dtype='<u2')
                delta = np.empty_like(row)
                delta[0] = row[0]
                np.subtract(row[1:], row[:-1], out=delta[1:])
                out.write(delta.tobytes())
    template = (ROOT / 'src/viewer.html').read_text()
    assert template.count('__COLOR__') == template.count('__HEIGHT__') == 1
    html = template.replace('__COLOR__', embed(color, 'image/jpeg')).replace('__HEIGHT__', embed(height, 'application/gzip'))
    output = ROOT / 'index.html'
    output.write_text(html)
    print(f'{output.name}: {output.stat().st_size / 1024**2:.1f} MiB')
    if output.stat().st_size >= 100 * 1024**2:
        raise SystemExit('Standalone exceeds GitHub single-file size limit')


if __name__ == '__main__':
    main()
