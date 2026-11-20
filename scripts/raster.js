// Rasterise land outlines into a pixel grid for the flow map.
// Output: land_grid.json {lon0, lat0, step, cols, rows, hex} where hex encodes row-major bits.
const fs = require('fs');
const topo = require('topojson-client');
const world = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const land = topo.feature(world, world.objects.land);
const LON0 = -150, LON1 = 160, LAT0 = 74, LAT1 = -56, STEP = 1.5;
const cols = Math.round((LON1 - LON0) / STEP), rows = Math.round((LAT0 - LAT1) / STEP);

const polys = [];
for (const f of land.features) {
  const g = f.geometry;
  const list = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
  for (const p of list) {
    const ring = p[0];
    let minx = 1e9, maxx = -1e9, miny = 1e9, maxy = -1e9;
    for (const [x, y] of ring) { minx = Math.min(minx, x); maxx = Math.max(maxx, x); miny = Math.min(miny, y); maxy = Math.max(maxy, y); }
    polys.push({ rings: p, minx, maxx, miny, maxy });
  }
}
function inRing(x, y, ring) {
  let ins = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i], [xj, yj] = ring[j];
    if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) ins = !ins;
  }
  return ins;
}
function inLand(x, y) {
  for (const p of polys) {
    if (x < p.minx || x > p.maxx || y < p.miny || y > p.maxy) continue;
    if (inRing(x, y, p.rings[0])) {
      let hole = false;
      for (let k = 1; k < p.rings.length; k++) if (inRing(x, y, p.rings[k])) { hole = true; break; }
      if (!hole) return true;
    }
  }
  return false;
}
const bits = [];
let count = 0;
for (let r = 0; r < rows; r++) {
  for (let c = 0; c < cols; c++) {
    const x0 = LON0 + c * STEP, y0 = LAT0 - r * STEP;
    let hit = 0;
    for (const [dx, dy] of [[.5, .5], [.25, .25], [.75, .25], [.25, .75], [.75, .75]]) {
      if (inLand(x0 + dx * STEP, y0 - dy * STEP)) hit++;
    }
    const b = hit >= 2 ? 1 : 0;
    bits.push(b); count += b;
  }
}
let hex = '';
for (let i = 0; i < bits.length; i += 4) {
  hex += ((bits[i] << 3) | ((bits[i + 1] || 0) << 2) | ((bits[i + 2] || 0) << 1) | (bits[i + 3] || 0)).toString(16);
}
fs.writeFileSync(process.argv[3], JSON.stringify({ lon0: LON0, lat0: LAT0, step: STEP, cols, rows, hex }));
console.log(cols, rows, count, 'land cells', hex.length, 'hex chars');
