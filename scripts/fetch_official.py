"""Download only Santa Catarina members of official TSE ZIPs via HTTP ranges."""
import io,struct,zipfile,zlib,subprocess,json,hashlib,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'research'; OUT.mkdir(exist_ok=True)
def get(url,start=None,end=None):
 cmd=['curl','-fLsS','--retry','2','--max-time','180']
 if start is not None: cmd+=['-H',('Range: bytes='+str(start) if start<0 else f'Range: bytes={start}-{end if end is not None else ""}')]
 return subprocess.check_output(cmd+[url])
def fetch(kind,year):
 name=f'{kind}_{year}';url=f'https://cdn.tse.jus.br/estatistica/sead/odsele/{('eleitorado_locais_votacao' if kind=='eleitorado_local_votacao' else kind)}/{name}.zip'; 
 if kind=='votacao_secao' and year>=2016: url=url.replace('.zip','_SC.zip')
 dest=OUT/f'{name}_SC.csv';meta=OUT/f'{name}.source.json'
 if dest.exists(): return (name,'cached',dest.stat().st_size)
 try:
  tail=get(url,-65536,'');pos=tail.rfind(b'PK\x05\x06');end=struct.unpack_from('<4s4H2LH',tail,pos);size,offset=end[5:7]
  central=get(url,offset,offset+size-1); idx=0;entries=[]
  while idx<len(central) and central[idx:idx+4]==b'PK\x01\x02':
   v=struct.unpack_from('<4s6H3L5H2L',central,idx);nl,xl,cl=v[10:13];fn=central[idx+46:idx+46+nl].decode('utf-8');entries.append((fn,v));idx+=46+nl+xl+cl
  match=[(fn,v) for fn,v in entries if fn.upper().endswith('_SC.CSV') or fn.upper().endswith('_SC.TXT')]
  if not match and kind=='eleitorado_local_votacao': match=[(fn,v) for fn,v in entries if fn.endswith('.csv')]
  if not match: return (name,'no SC member',[x[0] for x in entries][:8])
  fn,v=match[0];method,csize,off=v[4],v[8],v[16]
  header=get(url,off,off+29);lh=struct.unpack('<4s5H3L2H',header);data_start=off+30+lh[-2]+lh[-1]
  compressed=get(url,data_start,data_start+csize-1);raw=zlib.decompress(compressed,-15) if method==8 else compressed
  assert len(raw)==v[9] and zlib.crc32(raw)==v[7]
  dest.write_bytes(raw);meta.write_text(json.dumps({'url':url,'member':fn,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'accessedAt':'2026-10-07'},ensure_ascii=False,indent=2))
  return(name,'ok',len(raw))
 except Exception as e:return(name,'error',str(e))
if __name__=='__main__':
 import sys
 jobs=[(a.split(':')[0],int(a.split(':')[1])) for a in sys.argv[1:]]
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  for result in pool.map(lambda a:fetch(*a),jobs):print(result,flush=True)
