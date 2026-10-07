"""Validate independent geographic levels, eligibility and all published denominators."""
import json,math,csv
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'dist'
d=json.loads((P/'base-tratada.json').read_text());ss=json.loads((P/'secoes.json').read_text());results=[]
expected={2012:1491,2016:3326,2018:32512,2022:86568,2026:40327}
assert {e['year'] for e in d['elections']}==set(expected)
assert len(d['geography']['features'])==295
geocodes={f['properties']['codarea'] for f in d['geography']['features']}
for e in d['elections']:
 y=e['year'];t=e['totals'];ms=e['municipalities'];ns=e['neighborhoods'];ls=e['locations'];se=[s for s in ss if s['year']==y];city=next(m for m in ms if m['id']=='81051')
 assert t['votes']==expected[y]
 assert sum(m['votes'] for m in ms)==t['votes']
 assert len({m['id'] for m in ms})==len(ms)
 assert all(m['ibge'] in geocodes for m in ms)
 assert len(ms)==(1 if y<2018 else 295)
 assert sum(n['votes'] for n in ns)==sum(l['votes'] for l in ls)==sum(s['votes'] for s in se)==city['votes']
 assert len({(s['zone'],s['section']) for s in se})==len(se)
 assert len({n['id'] for n in ns})==len(ns)
 assert len({l['id'] for l in ls})==len(ls)
 for n in ns:
  linked=[l for l in ls if l['id'] in n['locationIds']]
  assert sum(l['votes'] for l in linked)==n['votes']
 for l in ls:
  linked=[s for s in se if s['locationId']==l['id']]
  assert sum(s['votes'] for s in linked)==l['votes']
 for m in ms:
  assert 0<=m['votes']<=m['validVotes']<=m['turnout']<=m['electorate']
  assert m['nominalVotes']+m['partyVotes']==m['validVotes']
  assert m['abstentions']+m['turnout']==m['electorate']
 if e['audit']['neighborhoodPercentagesAvailable']:
  assert sum(n['validVotes'] for n in ns)==city['validVotes']
  assert sum(s['validVotes'] for s in se)==city['validVotes']
  assert all(0<=n['votes']<=n['validVotes'] for n in ns)
 else:assert all(n['validVotes'] is None for n in ns) and all(s['validVotes'] is None for s in se)
 coverage=100*(city['votes']-sum(n['votes'] for n in ns if n['name']=='Não classificado'))/city['votes'];assert abs(coverage-e['audit']['classifiedVoteCoverage'])<1e-10
 if y==2026:
  for k in ['votes','validVotes','nominalVotes','partyVotes','turnout','electorate','sections','abstentions','blankVotes','nullVotes','subJudiceVotes','otherInvalidVotes']:
   assert sum(m[k] for m in ms)==t[k],(y,k,'state')
   assert sum(s[k] for s in se)==city[k],(y,k,'city')
 results.append({'year':y,'municipalities':len(ms),'sections':len(se),'candidateVotes':t['votes'],'cityVotes':city['votes'],'classificationCoverage':coverage,'validNeighborhoodDenominators':e['audit']['neighborhoodPercentagesAvailable']})
for stem,key in [('municipalities','municipalities'),('neighborhoods','neighborhoods'),('locations','locations')]:
 with (P/(stem+'.csv')).open(encoding='utf-8-sig') as f:csvrows=list(csv.DictReader(f,delimiter=';'))
 assert len(csvrows)==sum(len(e[key]) for e in d['elections'])
 assert sum(int(r['votos']) for r in csvrows)==sum(sum(r['votes'] for r in e[key]) for e in d['elections'])
print(json.dumps({'status':'passed','checks':'unique keys, 295 IBGE joins, candidate totals, section/location/neighborhood reconciliation, verified denominators, 2026 turnout and vote types, CSV integrity','elections':results},ensure_ascii=False,indent=2))
