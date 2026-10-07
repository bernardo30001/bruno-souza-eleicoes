import json,hashlib,sys
from pathlib import Path
from parse_bu import decode_file
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research'
manifest=json.loads((P/'manifesto-boletins-2026.json').read_text());out=[]
for m in manifest:
 path=Path(sys.argv[1])/m['arquivo'];raw=path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==m['sha256']
 r=decode_file(path);assert [r[k] for k in ('municipio','zona','secao')]==[81051,m['zona'],m['secao']]
 r['source']=m['url'];r['sha256']=m['sha256'];out.append(r)
(P/'inputs/boletins-2026.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
print(len(out),'official ballots decoded and verified')
