"""Build a list of PROPOSED changes for the mumok artist CSV.
Nothing is applied here. Output: proposed_changes.csv
"""
import csv, sys

SRC = sys.argv[1]
OUT = sys.argv[2]
rows = {r['artist_id']: r for r in csv.DictReader(open(SRC, encoding='utf-8-sig'))}

F = {'bde': 'cityofbirth_de', 'ben': 'cityofbirth_en', 'dde': 'cityofdeath_de',
     'den': 'cityofdeath_en', 'by': 'birthyear', 'dy': 'deathyear', 'nm': 'name'}

changes = []
def add(group, aid, f, new, note='', source=''):
    field = F.get(f, f)
    old = rows[aid][field]
    if old == new:
        return
    r = rows[aid]
    who = (r['firstname'] + ' ' + r['name']).strip()
    changes.append(dict(group=group, artist_id=aid, artist=who, field=field,
                        current=old, proposed=new, note=note, source=source))

# A. whitespace (auto)
for aid, r in rows.items():
    for k, v in r.items():
        nv = ' '.join(v.split()).replace(' ,', ',')
        if nv != v:
            add('A whitespace', aid, k, nv, 'extra spaces')

A = 'B spelling EN'
for aid, f, new in [
    ('36', 'ben', 'Copenhagen, Denmark'),
    ('113', 'ben', 'Tîrgu Mures, Romania'),
    ('743', 'ben', 'Brasov, Romania'), ('743', 'den', 'Brasov, Romania'),
    ('174', 'ben', 'Buenos Aires, Argentina'), ('1297', 'ben', 'Buenos Aires, Argentina'),
    ('294', 'ben', 'São Paulo, Brazil'), ('1618', 'ben', 'Caxias do Sul, Brazil'),
    ('871', 'ben', 'Luzzara, Reggio Emilia, Italy'), ('911', 'ben', 'Reggio Emilia, Italy'),
    ('618', 'ben', 'Rotterdam, The Netherlands'),
    ('183', 'ben', 'Sheffield, Great Britain'),
    ('2291', 'den', 'Stuttgart, Germany'), ('1479', 'ben', 'Stuttgart, Germany'),
    ('1957', 'ben', 'Prague, Czech Republic'),
    ('901', 'ben', 'Jindřichův Hradec, Czech Republic (then Neuhaus)'),
    ('2062', 'ben', 'Jerusalem, Israel'),
    ('1128', 'ben', 'Tehran, Iran'),
    ('2013', 'ben', 'Tehran, Iran'), ('2055', 'ben', 'Tehran, Iran'),
    ('3351', 'ben', 'Croix, France'),
    ('1929', 'ben', 'Tokyo, Japan'),
    ('1434', 'ben', 'Ostend, Belgium'),
    ('1478', 'ben', 'Antwerp, Belgium'),
    ('173', 'ben', 'Pontevedra, Galicia, Spain'),
    ('1444', 'ben', 'Vitebsk, Belarus'),
    ('21', 'ben', 'Batumi, Georgia'),
    ('831', 'ben', 'Lviv, Ukraine'),
    ('1818', 'ben', 'Orenburg, Russia'),
    ('216', 'ben', 'St. Tönis near Krefeld, Germany'),
    ('3201', 'ben', 'Hamburg, Germany'),
    ('1351', 'den', 'Vienna, Austria'),
    ('13', 'ben', 'Strasbourg, France (then Germany)'),
    ('1045', 'ben', 'Schneidemühl, Germany'),
    ('900', 'den', 'St. Martin an der Raab, Austria'),
]:
    add(A, aid, f, new)

U = 'C US place format'
for aid, f, new in [
    ('383', 'bde', 'Frankfort, IN, USA'), ('383', 'ben', 'Frankfort, IN, USA'),
    ('371', 'dde', 'Sacramento, CA, USA'), ('371', 'den', 'Sacramento, CA, USA'),
    ('2553', 'bde', 'Cleveland, OH, USA'), ('2553', 'ben', 'Cleveland, OH, USA'),
    ('2553', 'dde', 'New York, NY, USA'), ('2553', 'den', 'New York, NY, USA'),
    ('4620', 'bde', 'Cleveland, OH, USA'), ('4620', 'ben', 'Cleveland, OH, USA'),
    ('4505', 'bde', 'Newark, NJ, USA'), ('4505', 'ben', 'Newark, NJ, USA'),
    ('4505', 'dde', 'Dallas, TX, USA'), ('4505', 'den', 'Dallas, TX, USA'),
    ('508', 'dde', 'Vinalhaven, ME, USA'), ('508', 'den', 'Vinalhaven, ME, USA'),
    ('1237', 'dde', 'Rock Island, IL, USA'), ('1237', 'den', 'Rock Island, IL, USA'),
    ('3144', 'dde', 'Cincinnati, OH, USA'), ('3144', 'den', 'Cincinnati, OH, USA'),
    ('3033', 'bde', 'Tucson, AZ, USA'), ('3033', 'ben', 'Tucson, AZ, USA'),
    ('1016', 'dde', 'Hampton Bays, NY, USA'), ('1016', 'den', 'Hampton Bays, NY, USA'),
    ('1900', 'bde', 'Nevada, IA, USA'), ('1900', 'ben', 'Nevada, IA, USA'),
    ('461', 'bde', 'New York, NY, USA'),
]:
    add(U, aid, f, new, 'IO is not a state code, Iowa is IA' if aid == '1900' else 'consistent "City, ST, USA" format')

D = 'D spelling DE'
for aid, f, new in [
    ('1764', 'bde', 'Wien, Österreich'), ('2113', 'dde', 'Wien, Österreich'),
    ('1936', 'bde', 'Lindenberg, Deutschland'),
    ('801', 'bde', 'Libawka, Polen (damals Liebau, Deutschland)'),
    ('252', 'bde', 'Karlovy Vary (Karlsbad), Tschechische Republik'),
    ('1267', 'bde', 'Leeds, Großbritannien'),
    ('2062', 'bde', 'Jerusalem, Israel'),
    ('421', 'dde', 'Wien, Österreich'), ('820', 'dde', 'Wien, Österreich'),
    ('903', 'dde', 'Wien, Österreich'), ('1247', 'dde', 'Wien, Österreich'),
    ('747', 'bde', 'Wien, Österreich'),
]:
    add(D, aid, f, new)
for aid, r in rows.items():
    for k in ('cityofbirth_de', 'cityofdeath_de'):
        if 'Großbritanien' in r[k]:
            add(D, aid, k, r[k].replace('Großbritanien', 'Großbritannien'))

E = 'E malformed or missing EN'
for aid, f, new, note in [
    ('145', 'den', 'Ireland', 'EN was empty, DE says Irland'),
    ('461', 'ben', 'New York, NY, USA', 'EN was empty'),
    ('461', 'den', 'Compiègne, Oise, France', 'EN was empty'),
    ('747', 'ben', 'Vienna, Austria', 'EN was empty'),
    ('827', 'ben', 'Munich, Bavaria, Germany', 'EN was empty'),
    ('1934', 'ben', "'s-Hertogenbosch, The Netherlands", 'EN was empty'),
    ('1961', 'ben', 'Waldenstein', 'EN was empty, country not stated in source, left out'),
    ('1976', 'ben', 'Copenhagen / Kent', 'collective, EN was empty'),
    ('3142', 'bde', 'Wauwil LU, Schweiz', 'year was typed into the city field'),
    ('3142', 'ben', 'Wauwil LU, Switzerland', 'year was typed into the city field'),
    ('3143', 'bde', 'Tbilisi, Georgien', '"USA" wrongly appended'),
    ('3143', 'ben', 'Tbilisi, Georgia', '"USA" wrongly appended'),
    ('290', 'dde', 'Eisenstadt, Österreich', 'region instead of country'),
    ('290', 'den', 'Eisenstadt, Austria', 'region instead of country'),
    ('2036', 'dde', '', 'note "de Rijke: Ghana 2006" sits in the death-city field of a duo, move it to a notes column'),
    ('2', 'nm', 'Gelatin', 'lowercase, group is known today as Gelitin'),
]:
    add(E, aid, f, new, note)

FV = 'F fact fix (verified)'
for aid, f, new, note, src in [
    ('2430', 'by', '1893', 'Mayakovsky was born 19 July 1893', 'Wikipedia, Britannica'),
    ('312', 'by', '1893', 'born 9 Sept 1893 in Brno', 'MAK collection, Wikipedia'),
    ('312', 'dy', '1958', 'died 1958 in Salzburg (NGV lists 1950, MAK and others say 1958)', 'MAK, Wikipedia'),
    ('976', 'dy', '2017', 'died 5 Sept 2017 in Leipzig, death city already in data', 'Wikipedia, Städel'),
    ('1259', 'dy', '2015', 'died 7 Sept 2015 in Vienna, death city already in data', 'Austria-Forum, Der Standard'),
    ('2145', 'bde', 'Bern, ID, USA', 'born in Bern, Idaho, not Bern, Switzerland', 'Wikipedia, IRCAM'),
    ('2145', 'ben', 'Bern, ID, USA', 'born in Bern, Idaho, not Bern, Switzerland', 'Wikipedia, IRCAM'),
    ('1596', 'bde', 'Snovsk, Ukraine', 'DE says Russland, EN says Gomel', 'Wikipedia, Smithsonian'),
    ('1596', 'ben', 'Snovsk, Ukraine', 'DE and EN disagreed (Snovsk vs Gomel)', 'Wikipedia, Smithsonian'),
    ('1051', 'dde', 'Kendal, Großbritannien', 'died in Kendal hospital, lived in Ambleside, DE and EN disagreed', 'Schwitters Stiftung'),
    ('1051', 'den', 'Kendal, Great Britain', 'aligned with DE fix', 'Schwitters Stiftung'),
    ('1590', 'bde', 'Dublin, Irland', 'born 1945, Ireland was already independent', ''),
    ('1590', 'ben', 'Dublin, Ireland', 'born 1945, Ireland was already independent', ''),
    ('2246', 'bde', 'Dublin, Irland', 'born 1972', ''),
    ('2246', 'ben', 'Dublin, Ireland', 'born 1972', ''),
]:
    add(FV, aid, f, new, note, src)

FU = 'G likely typo (not yet verified)'
for aid, f, new, note in [
    ('141', 'bde', 'Centralia, WA, USA', 'Centrala looks like a typo'),
    ('141', 'ben', 'Centralia, WA, USA', 'Centrala looks like a typo'),
    ('641', 'bde', 'Plainfield, NJ, USA', 'Painfield looks like a typo'),
    ('641', 'ben', 'Plainfield, NJ, USA', 'Painfield looks like a typo'),
    ('922', 'bde', 'Ogikubo, Tokio, Japan', 'Ogibuko looks like a typo'),
    ('922', 'ben', 'Ogikubo, Tokyo, Japan', 'Ogibuko looks like a typo'),
    ('1237', 'bde', 'Window Rock, AZ, USA', 'Window Rock is in Arizona (AZ), not Arkansas (AR). His birthplace is also disputed'),
    ('1237', 'ben', 'Window Rock, AZ, USA', 'same as above'),
]:
    add(FU, aid, f, new, note)

# Policy items: listed, no change proposed until decided
P = 'H needs your decision'
policy = [
    ('49', 'cityofbirth_en', 'Francis Bacon born Dublin 1909, listed as Great Britain. Today: Ireland.'),
    ('2011', 'cityofbirth_en', 'Bethlehem listed under Israel.'),
    ('2059', 'cityofbirth_en', 'Gaza listed under Israel.'),
    ('1180', 'cityofdeath_en', 'Taiwan listed under China.'),
    ('1869', 'cityofbirth_en', 'Kyiv listed under Russia (born 1961, Ukrainian SSR). Also Kiev/Kiew/Kyiv spelled three ways in the file.'),
    ('227', 'name', 'Plamen Dejanov (id 227) and Plamen Dejanoff (id 2264): same birthplace and year, likely one person.'),
    ('465', 'cityofbirth_en', 'Dick Higgins: "Jesus Pieces, Cambridge" unclear, left as is.'),
]
for aid, field, note in policy:
    r = rows[aid]
    changes.append(dict(group=P, artist_id=aid, artist=(r['firstname'] + ' ' + r['name']).strip(),
                        field=field, current=r[field], proposed='(your call)', note=note, source=''))

with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['group', 'artist_id', 'artist', 'field', 'current', 'proposed', 'note', 'source'])
    w.writeheader()
    for c in sorted(changes, key=lambda c: (c['group'], int(c['artist_id']))):
        w.writerow(c)

import collections
print(collections.Counter(c['group'] for c in changes))
print(len(changes), 'rows written')
