"""Inject charts/local.json into the app page (in place, re-runnable)."""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
APP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'app', 'index.html')
date = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().strftime('%-d %b %Y')

data = json.load(open(os.path.join(HERE, 'local.json'), encoding='utf-8'))
blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
s = open(APP, encoding='utf-8').read()
s, n1 = re.subn(r'/\*LOCAL\*/.*?/\*END\*/', lambda m: '/*LOCAL*/' + blob + '/*END*/', s, flags=re.S)
s, n2 = re.subn(r"var DATA_DATE = '[^']*';", "var DATA_DATE = '%s';" % date, s)
assert n1 == 1 and n2 == 1, (n1, n2)
open(APP, 'w', encoding='utf-8').write(s)
print('injected', len(data), 'countries,', sum(len(v) for v in data.values()), 'songs, dated', date)
