// Match birth and death places of the cleaned mumok list to GeoNames cities (all-the-cities, pop > 1000).
// Usage: node geocode.js <clean.csv> <out.json> <report.csv> [manual.json]
const fs = require('fs');
const cities = require('all-the-cities');
const [, , SRC, OUT, REPORT, MANUAL] = process.argv;
const PA = JSON.parse(fs.readFileSync(__dirname + '/place_aliases.json', 'utf8'));
const manual = MANUAL && fs.existsSync(MANUAL) ? JSON.parse(fs.readFileSync(MANUAL, 'utf8')) : {};

const ISO = { Austria: 'AT', Germany: 'DE', France: 'FR', Italy: 'IT', Spain: 'ES', Portugal: 'PT', Switzerland: 'CH', 'The Netherlands': 'NL', Belgium: 'BE', 'United Kingdom': 'GB', Ireland: 'IE', Denmark: 'DK', Sweden: 'SE', Norway: 'NO', Finland: 'FI', Iceland: 'IS', 'Czech Republic': 'CZ', Slovakia: 'SK', Hungary: 'HU', Poland: 'PL', Slovenia: 'SI', Croatia: 'HR', Serbia: 'RS', 'Bosnia and Herzegovina': 'BA', 'North Macedonia': 'MK', Albania: 'AL', Romania: 'RO', Bulgaria: 'BG', Moldova: 'MD', Ukraine: 'UA', Belarus: 'BY', Lithuania: 'LT', Latvia: 'LV', Estonia: 'EE', Russia: 'RU', Georgia: 'GE', Azerbaijan: 'AZ', Turkmenistan: 'TM', Greece: 'GR', Turkey: 'TR', Israel: 'IL', 'Palestinian Territories': 'PS', Malta: 'MT', Liechtenstein: 'LI', USA: 'US', Canada: 'CA', Mexico: 'MX', Cuba: 'CU', Venezuela: 'VE', Colombia: 'CO', Peru: 'PE', Chile: 'CL', Argentina: 'AR', Uruguay: 'UY', Brazil: 'BR', Japan: 'JP', 'South Korea': 'KR', China: 'CN', Taiwan: 'TW', India: 'IN', Bangladesh: 'BD', Iran: 'IR', Iraq: 'IQ', Egypt: 'EG', Libya: 'LY', Kenya: 'KE', 'South Africa': 'ZA', Australia: 'AU', 'New Zealand': 'NZ', 'French Polynesia (France)': 'PF' };
const ALIAS = {'new york': 'New York City', 'brooklyn': 'Brooklyn', 'manhattan': 'Manhattan', cologne: 'Köln', geneva: 'Genève', klagenfurt: 'Klagenfurt am Wörthersee', torino: 'Turin', milano: 'Milan', antwerp: 'Antwerpen', lucerne: 'Luzern', nuremberg: 'Nürnberg', hanover: 'Hannover', kiev: 'Kyiv', kiew: 'Kyiv', padua: 'Padova', 'reggio emilia': 'Reggio nell\'Emilia', 'san sebastian': 'Donostia / San Sebastián', 'santiago de chile': 'Santiago', ploesti: 'Ploieşti', 'st polten': 'Sankt Pölten', 'saint polten': 'Sankt Pölten', 'palma de mallorca': 'Palma', 'lodz': 'Łódź', 'tallin': 'Tallinn', 'freiburg im breisgau': 'Freiburg', biel: 'Biel/Bienne', 'bruck mur': 'Bruck an der Mur', krems: 'Krems an der Donau', braunau: 'Braunau am Inn', meran: 'Merano', schlanders: 'Silandro', 'dnjepropetrowsk': 'Dnipro', 'viipuri': 'Vyborg', 'leningrad': 'Saint Petersburg', 'wroclaw': 'Wrocław', 'meissen': 'Meißen', 'gwardeisk': 'Gvardeysk', 'oran': 'Oran', 'minieh': 'Al Minyā', 'shkodra': 'Shkodër', 'battlecreek': 'Battle Creek', 'glenn ridge': 'Glen Ridge', 'werwik': 'Wervik', 'okoyama': 'Okayama', 'torschok': 'Torzhok', 'druskieniki': 'Druskininkai', 'neutra': 'Nitra', 'rechovot': 'Rehovot', 'qingtian': 'Qingtian', 'wattenscheid': 'Wattenscheid', 'bad godesberg': 'Bad Godesberg'};
const US = { Alabama: 'AL', Arizona: 'AZ', Tennessee: 'TN', Iowa: 'IA' };

const norm = (s) => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/ß/g, 'ss').replace(/^(st\.|saint |sankt |st )\s*/, 'st ').replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
const idx = new Map();
for (const c of cities) {
  for (const n of [c.name, ...(c.altName ? c.altName.split(',') : [])]) {
    const k = norm(n) + '|' + c.country;
    const prev = idx.get(k);
    if (!prev || c.population > prev.population) idx.set(k, c);
  }
}
const byCountry = new Map(); for (const c of cities) { if (!byCountry.has(c.country)) byCountry.set(c.country, []); byCountry.get(c.country).push(c); }
const usIdx = new Map();
for (const c of cities) if (c.country === 'US') { const k = norm(c.name) + '|' + c.adminCode; const p = usIdx.get(k); if (!p || c.population > p.population) usIdx.set(k, c); }

const parseCsv = (text) => {
  const rows = []; let row = [], f = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) { if (ch === '"') { if (text[i + 1] === '"') { f += '"'; i++; } else q = false; } else f += ch; }
    else if (ch === '"') q = true; else if (ch === ',') { row.push(f); f = ''; } else if (ch === '\n') { row.push(f); rows.push(row); row = []; f = ''; } else if (ch !== '\r') f += ch;
  }
  if (f || row.length) { row.push(f); rows.push(row); }
  const head = rows.shift();
  return rows.filter((r) => r.length === head.length).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])));
};

const rows = parseCsv(fs.readFileSync(SRC, 'utf8'));
const report = [['artist_id', 'kind', 'place_en', 'city', 'country', 'match', 'lat', 'lon', 'matched_name']];

function locate(r, kind) {
  const full = kind === 'birth' ? r.cityofbirth_en || r.cityofbirth_de : r.cityofdeath_en || r.cityofdeath_de;
  const city = kind === 'birth' ? r.birth_city : r.death_city;
  const country = kind === 'birth' ? r.birth_country : r.death_country;
  const mk = r.artist_id + ':' + kind;
  if (manual[mk]) { const m = manual[mk]; report.push([r.artist_id, kind, full, city, country, 'manual', m.lat, m.lon, m.name]); return { lat: m.lat, lon: m.lon, precision: m.precision || 'city', label: m.label || full }; }
  if (!full) return null;
  if (PA[full]) { const [nm, cc, pr, ad] = PA[full]; const h = cities.filter((x) => x.country === cc && x.name === nm && (!ad || x.adminCode === ad)).sort((p, q) => q.population - p.population)[0]; if (h) { report.push([r.artist_id, kind, full, city, country, pr === 'near' ? 'near' : 'alias', h.loc.coordinates[1], h.loc.coordinates[0], h.name]); return { lat: h.loc.coordinates[1], lon: h.loc.coordinates[0], precision: pr, label: full, near: pr === 'near' ? h.name : null }; } }
  const iso = ISO[country];
  let hit = null;
  const parts = full.replace(/\([^)]*\)/g, '').split(',').map((s) => s.trim()).filter(Boolean);
  if (iso === 'US' && parts.length >= 3) {
    let st = parts[parts.length - 2]; st = US[st] || st;
    hit = usIdx.get(norm(ALIAS[norm(parts[0])] || parts[0]) + '|' + st) || usIdx.get(norm(parts[0]) + '|' + st);
  }
  const de = (kind === 'birth' ? r.cityofbirth_de : r.cityofdeath_de) || '';
  const base = [city, (city || '').split(/ near | bei |\/| \(/)[0], parts[0], de.split(',')[0].replace(/\([^)]*\)/g, '').trim()].filter(Boolean);
  const tries = [];
  for (const t of base) { tries.push(t); const a = ALIAS[norm(t)]; if (a) tries.unshift(a); tries.push(t.replace(/^(Bad|Schloß|Schloss|Maria) /, '')); }
  for (const t of tries) { if (hit) break; if (iso) hit = idx.get(norm(t) + '|' + iso); }
  if (hit) { report.push([r.artist_id, kind, full, city, country, 'city', hit.loc.coordinates[1], hit.loc.coordinates[0], hit.name]); return { lat: hit.loc.coordinates[1], lon: hit.loc.coordinates[0], precision: 'city', label: full }; }
  if (iso) {
    const words = [...new Set(tries.map((t) => norm(t)))].filter((t) => t.length >= 4);
    let best = null;
    for (const c of byCountry.get(iso) || []) { const n = norm(c.name); for (const w of words) { const ok = n.replace(/ /g, '') === w.replace(/ /g, '') || (n.startsWith(w + ' ') && w.length >= 6) || (w.startsWith(n + ' ') && n.length >= 7 && /^(im|am|an|in|a d|ob|bei) /.test(w.slice(n.length + 1))); if (ok && (!best || c.population > best.population)) best = c; } }
    if (best) { report.push([r.artist_id, kind, full, city, country, 'loose', best.loc.coordinates[1], best.loc.coordinates[0], best.name]); return { lat: best.loc.coordinates[1], lon: best.loc.coordinates[0], precision: 'city', label: full }; }
  }
  report.push([r.artist_id, kind, full, city, country, 'NONE', '', '', '']);
  return null;
}

const out = [];
for (const r of rows) {
  const b = locate(r, 'birth');
  const d = locate(r, 'death');
  out.push({ id: r.artist_id, who: [r.firstname, r.name].filter(Boolean).join(' '), type: r.entity_type, born: r.birthyear ? +r.birthyear : null, died: r.deathyear ? +r.deathyear : null, born_place: r.cityofbirth_en || r.cityofbirth_de || null, died_place: r.cityofdeath_en || r.cityofdeath_de || null, born_country: r.birth_country || null, died_country: r.death_country || null, born_lat: b ? +(+b.lat).toFixed(3) : null, born_lon: b ? +(+b.lon).toFixed(3) : null, died_lat: d ? +(+d.lat).toFixed(3) : null, died_lon: d ? +(+d.lon).toFixed(3) : null, born_precision: b ? b.precision : null, died_precision: d ? d.precision : null, born_near: b && b.near ? b.near : null, died_near: d && d.near ? d.near : null, flag: r.data_flag || null });
}
fs.writeFileSync(OUT, JSON.stringify(out));
fs.writeFileSync(REPORT, report.map((r) => r.map((v) => '"' + String(v).replace(/"/g, '""') + '"').join(',')).join('\n'));
const none = report.filter((r) => r[5] === 'NONE');
console.log('places', report.length - 1, 'unmatched', none.length);
console.log(none.map((r) => r[0] + ':' + r[1] + ' | ' + r[2] + ' | ' + r[4]).join('\n'));
