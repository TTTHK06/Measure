# RoomScan

Photograph a room on a phone, get real dimensions, get a 3D model. Plain HTML, CSS and
JavaScript — no build step, no npm, no CDN, no libraries. Works offline once loaded.

```bash
py serve.py
```

Then open `http://localhost:8777` on this machine, or `http://<lan-ip>:8777` on a phone on the
same Wi-Fi (the server prints the address).

---

## What it actually does

This is **single-view metrology**, not lidar and not ARKit/ARCore. A browser cannot access a
phone's depth sensor or AR tracking, so dimensions are recovered from geometry that *is*
available: a known reference object, or the phone's tilt sensors plus a calibrated camera.
Three routes feed one room model.

### 1 · Photo (works everywhere — no permissions, no https)

Put something of known size flat on the floor (A4 sheet, floor tile, 1 m tape square).
Photograph the room so the reference and the floor corners are both visible.

1. Tap the reference's four corners: **near-left, near-right, far-right, far-left**.
   A green 1 m grid is projected onto the floor — if it doesn't lie flat, nudge the corners.
2. Tap each floor corner of the room. Wall lengths appear live.
3. **Use corners as room.**

Solves a homography from the photo's floor plane to the real floor plane. Exact in theory —
in practice limited by how precisely you can tap (±1 px tapping ≈ ±10 mm at 4 m in testing)
and by how far the corners are from the reference. Bigger reference = better.

### 2 · Scan (live camera + tilt sensors — needs https)

Stand in one spot. The crosshair shows a live distance to the floor. Aim where the wall meets
the floor and **Mark corner**, turning on the spot until the room closes. **Ceiling ht** then
sights the wall/ceiling line above the last corner.

Needs two calibrations, once per phone (**Calibrate…**):

- **A — you know your phone height.** Mark a spot on the floor a tape-measured distance in
  front of your toes, aim at it, solve. Recovers focal length.
- **B — two marks.** Two measured distances (say 1 m and 3 m). Recovers focal length *and*
  phone height, no tape on yourself needed.

Can't see every corner from one spot? **New spot…** — walk, re-sight two corners you already
measured, and the app resects your new position and keeps one continuous plan. It reports a
baseline check (measured vs known) so you can see the error you're carrying.

### 3 · Plan (tape measure — the accurate one)

**Rectangle…** for a rectangular room, or tap any wall and type its true length. A typed length
is **locked** (🔒). **Square up** then snaps wall directions to 90° while holding the locked
lengths exactly, so photo/scan estimates get pulled onto the measurements you trust.

**Mixing routes is the recommended workflow**: photo- or scan-capture the shape, tape one or
two walls, lock them, square up.

---

## Then

- **Plan tab** — drag corners, insert/delete them, add doors and windows per wall (offset,
  width, sill, head), ortho and 50 mm grid snapping, live dimensions, angles, area, scale bar.
- **3D tab** — orbit/pinch/pan, ceiling on/off, inside view, top view. Openings are real
  cutouts with reveals. Wall photos can be rectified and applied as textures
  (**Photo → 3 · Wall photo**, or **Grab photo** from the scan view).
- **Export tab** — GLB (Blender / Windows 3D Viewer / SketchUp / phone AR, textures embedded),
  OBJ+MTL zip with texture files, SVG floor plan with dimensions and a title block, CSV wall
  schedule (lengths, net areas, openings, bearings), and JSON to reload later. Rooms save to
  the browser and to named slots.

## Accuracy, honestly

| Route | Typical | Dominated by |
|---|---|---|
| Photo | ±1–3 % near the reference | tap precision, reference size, distance from reference |
| Scan | ±2–5 % | calibration, compass drift while turning, sensor noise |
| Tape + lock + square up | as good as your tape | you |

Sanity-check one wall against a tape the first time you use a new phone. A consistent
percentage error means the calibration is off, not the method.

## Getting https on a phone (scan mode only)

Browsers block the camera and motion sensors on plain `http://` from another device.
`localhost` is exempt, a LAN IP is not. Either:

```bash
cloudflared tunnel --url http://localhost:8777
```

```bash
ngrok http 8777
```

and open the tunnel's `https://…` URL on the phone. The **Photo** tab needs none of this — it
uses the normal camera app through a file input.

## Files

```
index.html          shell + all views
css/app.css         mobile-first dark UI, safe-area insets
js/mathx.js         homography/DLT, ray↔floor-plane, triangulation, regularization
js/sensors.js       orientation permission, tilt/heading → quaternion, camera stream
js/store.js         room model, walls, openings, locks, undo, localStorage
js/plan.js          2D plan editor
js/photo.js         reference-rectangle metrology + wall rectification
js/scan.js          live camera measurement, calibration solvers, station resection
js/render3d.js      mesh builder + dependency-free WebGL renderer
js/exporters.js     GLB, OBJ+MTL+zip, SVG, CSV, JSON
serve.py            no-cache dev server
```

## Limitations

- One room at a time; save to a slot and start another.
- Floors are assumed flat and walls vertical — measurements are taken on the floor plane.
- Scan mode inherits compass drift; mark all corners from one spot where you can, and use
  **New spot…** rather than walking silently.
- Sloped ceilings, curved walls and wall thickness aren't modelled (single-line walls).
