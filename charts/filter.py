"""Build local-only song lists per country from kworb chart snapshots.

A song is treated as international (and dropped) if it:
  - appears in the Top 50 of 3+ of the fetched countries, or
  - is on the Global Top 200 AND in the Top 50 of 2+ fetched countries.
Songs are matched by Spotify track ID or by a normalised "artist - title" key,
so a garbled ID still matches by name.
"""
import json, os, re, sys, unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_SONGS = 5
SKIP = re.compile(r'white noise|sleep sound|christmas|xmas|jingle|santa|let it snow|snowman|wonderful time of the year|underneath the tree|vaggvisa|godnatt|humlan djojj|babblarna|lullaby', re.I)
REF_NAMES = {'AU':'Australia','CA':'Canada','IE':'Ireland','AT':'Austria','NO':'Norway'}

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(w/[^)]*\)|\(feat[^)]*\)|\(with[^)]*\)', '', s)
    s = re.sub(r' - (ao vivo|en vivo|remaster.*|live.*)$', '', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()

def load():
    glob = set(open(os.path.join(HERE, 'global.txt')).read().split())
    charts = {}
    for f in sorted(os.listdir(HERE)):
        m = re.fullmatch(r'([A-Z]{2})\.txt', f)
        if not m: continue
        rows, seen = [], set()
        for line in open(os.path.join(HERE, f), encoding='utf-8'):
            line = line.strip()
            if '|' not in line: continue
            tid, name = line.split('|', 1)
            if ' - ' not in name or SKIP.search(name): continue
            k = norm(name)
            if k in seen: continue
            seen.add(k)
            rows.append((tid.strip(), name.strip(), k))
        charts[m.group(1)] = rows
    refs = {}
    for f in sorted(os.listdir(HERE)):
        m = re.fullmatch(r'ref_([A-Z]{2})\.txt', f)
        if m: refs[m.group(1)] = set(open(os.path.join(HERE, f)).read().split())
    return glob, charts, refs

def build():
    glob, charts, refs = load()
    where = defaultdict(set)              # key -> countries
    for cc, ids in refs.items():
        for tid in ids: where['id:' + tid].add(cc)
    for cc, rows in charts.items():
        for tid, name, k in rows:
            where['id:' + tid].add(cc); where['n:' + k].add(cc)
    out, report = {}, {}
    for cc, rows in charts.items():
        # Countries whose charts are mostly global songs: any global-chart song counts as international.
        share = sum(1 for tid, _, _ in rows if tid in glob) / max(1, len(rows))
        strict = share > 0.4
        keep = []
        for tid, name, k in rows:
            cs = where['id:' + tid] | where['n:' + k]
            n = len(cs)
            if n >= 3 or (tid in glob and (n >= 2 or strict)):
                continue
            artist, title = name.split(' - ', 1)
            keep.append([artist, title, sorted(cs - {cc})])
        report[cc] = len(keep)
        if len(keep) >= MIN_SONGS:
            out[cc] = keep
    return out, report

if __name__ == '__main__':
    out, report = build()
    json.dump(out, open(os.path.join(HERE, 'local.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for cc, n in sorted(report.items(), key=lambda x: x[1]):
        print(cc, n, '' if cc in out else '(dropped)')
