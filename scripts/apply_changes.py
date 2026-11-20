"""Apply APPROVED changes to a new cleaned copy and add helper columns.
Approved (2026-11-20): groups A-E, helper columns, today's country + historical note,
place-based names for contested places, Dejanov/Dejanoff kept and flagged.
Not applied: group F (verified fact fixes), G (unverified typos). Those rows get a flag.
"""
import csv, re, sys, collections

SRC, PROPOSED, OUT, LOG = sys.argv[1:5]
APPLY = ('A ', 'B ', 'C ', 'D ', 'E ')

src = list(csv.DictReader(open(SRC, encoding='utf-8-sig')))
fields = list(src[0].keys())
rows = {r['artist_id']: dict(r) for r in src}
log = []

def setv(aid, field, new, why):
    old = rows[aid][field]
    if old != new:
        rows[aid][field] = new
        log.append(dict(artist_id=aid, field=field, old=old, new=new, reason=why))

# 1. groups A-E from the reviewed proposal
for p in csv.DictReader(open(PROPOSED, encoding='utf-8')):
    if p['group'].startswith(APPLY):
        assert rows[p['artist_id']][p['field']] == p['current'] or p['group'].startswith('A'), p
        setv(p['artist_id'], p['field'], p['proposed'], p['group'] + ': ' + (p['note'] or 'fix'))
# whitespace fixes may have been listed before a later fix on the same field, re-run whitespace on all
for aid, r in rows.items():
    for k, v in r.items():
        nv = ' '.join(v.split()).replace(' ,', ',')
        if nv != v:
            setv(aid, k, nv, 'A whitespace')

# 2. contested places, place-based names (approved)
C = 'contested place, place-based name (approved)'
setv('2011', 'cityofbirth_de', 'Bethlehem, Palästinensische Gebiete', C)
setv('2011', 'cityofbirth_en', 'Bethlehem, Palestinian Territories', C)
setv('2059', 'cityofbirth_de', 'Gaza, Palästinensische Gebiete', C)
setv('2059', 'cityofbirth_en', 'Gaza, Palestinian Territories', C)
setv('1180', 'cityofdeath_de', 'Taiwan', C)
setv('1180', 'cityofdeath_en', 'Taiwan', C)
setv('1869', 'cityofbirth_de', 'Kiew, Ukraine', C)
setv('1869', 'cityofbirth_en', 'Kyiv, Ukraine', C)

# 3. helper columns -------------------------------------------------------
COUNTRY = {  # source label -> today's country
    'Great Britain': 'United Kingdom', 'England': 'United Kingdom', 'UK': 'United Kingdom',
    'Slovak Republic': 'Slovakia', 'Bosnia': 'Bosnia and Herzegovina',
    'Macedonia': 'North Macedonia', 'Republic of Macedonia': 'North Macedonia',
    "The People's Republic of China": 'China', 'Asia': None,
    'Marquesas-Islands': 'French Polynesia (France)', 'Northern Bohemia': 'Czech Republic',
}
CITY_COUNTRY = {  # historical or ambiguous places -> today's country
    'Dvur Králové nad Labem': 'Czech Republic', 'Olomouc': 'Czech Republic',
    'Protivín': 'Czech Republic', 'Opocno': 'Czech Republic',
    'Czernowitz': 'Ukraine', 'Strasbourg': 'France', 'Straßburg': 'France',
    'Schneidemühl': 'Poland', 'Insterburg': 'Russia', 'Dublin': 'Ireland',
    'Gomel': 'Belarus', 'Turkmenistan': 'Turkmenistan',
}
HIST = {  # today's country differs from what the record names, note why
    'Dublin': 'then United Kingdom (pre-1922 births)', 'Schneidemühl': 'then Germany, today Piła',
    'Insterburg': 'then Germany, today Chernyakhovsk', 'Strasbourg': 'then Germany',
    'Straßburg': 'then Germany',
}
SPECIAL = {
    ('1061', 'death'): ('Pyrenees', None, 'missing in the Pyrenees, Spain or France'),
    ('496', 'death'): ('at sea', None, 'aboard the RMS Queen Elizabeth 2, near New Zealand'),
    ('845', 'birth'): ('Wrocław', 'Poland', 'then Breslau, Germany'),
    ('2431', 'death'): ('St. Petersburg', 'Russia', 'then Leningrad'),
    ('1976', 'birth'): ('Copenhagen / Kent', None, 'collective, two places'),
    ('1961', 'birth'): ('Waldenstein', None, 'country not stated in source'),
}

def parse(aid, kind, text):
    if (aid, kind) in SPECIAL:
        return SPECIAL[(aid, kind)]
    if not text:
        return ('', None, '')
    notes = re.findall(r'\(([^)]*)\)', text)
    base = re.sub(r'\s*\([^)]*\)', '', text).strip().strip(',')
    parts = [p.strip() for p in base.split(',') if p.strip()]
    city = parts[0] if len(parts) > 1 else ''
    label = parts[-1]
    if label in ('USA',):
        country = 'USA'
    elif label in COUNTRY:
        country = COUNTRY[label]
    elif label == 'Austria-Hungary':
        country = CITY_COUNTRY.get(city)
    else:
        country = label
    if city in CITY_COUNTRY:
        country = CITY_COUNTRY[city]
    if label == 'Asia':
        city, country = parts[0], 'Turkmenistan'
    note = '; '.join(notes)
    if city in HIST:
        note = (note + '; ' if note else '') + HIST[city]
    if label == 'Austria-Hungary':
        note = (note + '; ' if note else '') + 'then Austria-Hungary'
    if label == 'Northern Bohemia':
        note = (note + '; ' if note else '') + 'then Bohemia'
    if not city and len(parts) == 1:
        city = ''
    return (city, country, note)

COLLECTIVES = {'2', '16', '117', '355', '446', '512', '811', '1217', '1411', '1412', '1571',
               '1917', '1976', '2036', '2048', '2049', '2061', '2112', '2119', '2218', '2258',
               '2272', '2278', '2284', '2330', '2350', '4335'}
NOT_PERSON_NOTE = {'2258': 'gallery', '2278': 'TV station', '2119': 'school'}

FLAGS = {
    '2430': 'suspect birthyear: sources give 1893 (fix not applied)',
    '312': 'suspect years: sources give 1893-1958 (fix not applied)',
    '976': 'death year missing: sources give 2017 (fix not applied)',
    '1259': 'death year missing: sources give 2015 (fix not applied)',
    '2145': 'suspect birthplace: sources give Bern, Idaho (fix not applied)',
    '1596': 'suspect birthplace: sources give Snovsk, Ukraine (fix not applied)',
    '1051': 'death place: sources give Kendal (fix not applied)',
    '1590': 'Dublin 1945 listed as Great Britain in text fields',
    '2246': 'Dublin 1972 listed as Great Britain in text fields',
    '141': 'likely typo Centrala/Centralia (not applied)',
    '641': 'likely typo Painfield/Plainfield (not applied)',
    '922': 'likely typo Ogibuko/Ogikubo (not applied)',
    '1237': 'Window Rock is in AZ not AR, birthplace disputed (not applied)',
    '227': 'same person as id 2264 (Dejanoff), count once',
    '2264': 'same person as id 227 (Dejanov), count once',
    '465': 'birthplace text unclear ("Jesus Pieces")',
    '2011': 'contested place, label changed', '2059': 'contested place, label changed',
    '1180': 'contested place, label changed', '1869': 'contested place, label changed',
}
NOTES = {'2036': 'de Rijke: Ghana 2006 (moved from death-city field)'}

extra = ['entity_type', 'birth_city', 'birth_country', 'birth_hist_note',
         'death_city', 'death_country', 'death_hist_note',
         'lifespan', 'birth_decade', 'count_once_group', 'data_flag', 'note']
out_rows = []
for r in src:
    aid = r['artist_id']
    x = dict(rows[aid])
    bc, bco, bn = parse(aid, 'birth', x['cityofbirth_en'] or x['cityofbirth_de'])
    dc, dco, dn = parse(aid, 'death', x['cityofdeath_en'] or x['cityofdeath_de'])
    x['entity_type'] = 'collective' if aid in COLLECTIVES else 'person'
    if aid in NOT_PERSON_NOTE:
        x['entity_type'] = 'collective/other'
    x.update(birth_city=bc, birth_country=bco or '', birth_hist_note=bn,
             death_city=dc, death_country=dco or '', death_hist_note=dn)
    by, dy = x['birthyear'], x['deathyear']
    x['lifespan'] = str(int(dy) - int(by)) if by.isdigit() and dy.isdigit() else ''
    x['birth_decade'] = str(int(by) // 10 * 10) if by.isdigit() else ''
    x['count_once_group'] = 'dejanov' if aid in ('227', '2264') else ''
    x['data_flag'] = FLAGS.get(aid, '')
    if not by and not x['cityofbirth_en'] and x['entity_type'] == 'person':
        x['data_flag'] = (x['data_flag'] + '; ' if x['data_flag'] else '') + 'no birth data'
    x['note'] = NOTES.get(aid, '')
    out_rows.append(x)

with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=fields + extra)
    w.writeheader(); w.writerows(out_rows)
with open(LOG, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['artist_id', 'field', 'old', 'new', 'reason'])
    w.writeheader(); w.writerows(log)
print(len(out_rows), 'rows,', len(log), 'changes applied')
