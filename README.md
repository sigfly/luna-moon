# Luna — Interactive 3D Moon Atlas

A standalone WebGL 2 Moon viewer with embedded NASA Lunar Reconnaissance Orbiter imagery and elevation data. [Download index.html](https://github.com/sigfly/luna-moon/raw/refs/heads/main/index.html) and open it in a modern browser. No server, build step, dependencies, or internet connection are required to use the generated file. The high-resolution download is approximately 90 MiB.

## High-resolution edition

| Map | NASA source | Embedded resolution | Equatorial sampling |
| --- | --- | --- | --- |
| Color | December 2025 LROC CGI Moon Kit color, 16-bit sRGB TIFF | 16,384 × 8,192 (JPEG) | 666 m/pixel |
| Elevation | LOLA 64 pixels/degree, 23,040 × 11,520 unsigned TIFF | 8,192 × 4,096 (losslessly compressed 16-bit samples) | 1,333 m/pixel |

The NASA elevation source is averaged to the embedded grid. Samples are stored using the NASA half-meter encoding (height above the 1,737.4 km reference sphere = sample × 0.5 m − 10,000 m). The globe uses metric displacement and surface slopes, adjustable exaggeration, and an elevation legend in kilometers. Color is converted from 16-bit sRGB to 8-bit JPEG for browser compatibility. The sphere is tessellated separately from the much finer elevation texture, so small details are represented primarily through lighting rather than geometric silhouettes.

On capable desktop GPUs, the texture reaches 16K; on touch devices or devices reporting low memory, it is reduced to 4K. The actual loaded resolution is shown in the sidebar. A modern WebGL 2 browser with gzip DecompressionStream support and hardware acceleration is recommended. Large maps may need substantial RAM and GPU memory. For navigation, zoom extends to 16×.

## Features

- Rotate, zoom, and explore both lunar hemispheres and poles.
- Natural-color and relative-elevation views, adjustable terrain relief, coordinate grid, lunar phase lighting, and shadow fill.
- Interactive landmarks, including all six crewed Apollo landing sites.
- Auto-rotation, fullscreen, and PNG screenshot export.

## Development

The editable application is `src/viewer.html`. `assets/` holds the separate processed color and elevation maps. Generate the embedded standalone file after editing:

```sh
python -m pip install numpy
python tools/build.py
```

The Python builder requires GDAL's `gdal_translate` on PATH if the processed assets are missing, and downloads the original NASA TIFFs into the ignored `.cache/` directory. Gzip row differences preserve the resampled unsigned 16-bit elevation samples exactly. The committed `index.html` is generated, not the editable source. Do not paste or inspect its base64 assets as text.

An optional offline-browser smoke test is provided (`node tools/smoke-test.cjs`, requires Playwright and Chromium); it checks the globe renders and several controls respond while blocking HTTP/HTTPS requests.

## Data credit

NASA Scientific Visualization Studio, [CGI Moon Kit](https://svs.gsfc.nasa.gov/4720), visualization by Ernie Wright, based on the LROC WAC Hapke-normalized mosaic and LOLA elevation data. NASA's color composite uses lower-resolution monochromatic albedo information outside ±70° latitude, so polar color detail is not equivalent to equatorial coverage. The terrain and approximate lighting are intended for visualization rather than scientific measurement or live ephemerides. For higher-resolution local regions, consult [LROC QuickMap](https://quickmap.lroc.asu.edu/); this atlas does not resolve individual Apollo equipment.
