"""Reduce the downloaded official extracts to the public data used by this dashboard."""
import csv,json,concurrent.futures,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'research';D=P/'inputs';D.mkdir(exist_ok=True)
def save(name,obj): (D/name).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')))
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.upper()) if unicodedata.category(c)!='Mn')
keepers=['DT_GERACAO','HH_GERACAO','ANO_ELEICAO','NR_TURNO','CD_ELEICAO','DT_ELEICAO','NM_UE','DS_CARGO','CD_CARGO','SQ_CANDIDATO','NR_CANDIDATO','NM_CANDIDATO','NM_URNA_CANDIDATO','SG_PARTIDO','DT_NASCIMENTO','DS_SIT_TOT_TURNO','DS_SITUACAO_CANDIDATURA']
check=[]
for f in sorted(P.glob('consulta_cand_*_SC.csv')):
 with f.open(encoding='latin1') as inp:
  rows=[{k:v for k,v in r.items() if k in keepers} for r in csv.DictReader(inp,delimiter=';') if norm(r['NM_CANDIDATO'])=='BRUNO ANDRE DE SOUZA' and r['DT_NASCIMENTO']=='20/08/1984']
 check.append({'year':int(f.name.split('_')[2]),'matches':rows,'source':f'https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{f.name.split("_")[2]}.zip'})
save('candidaturas.json',check)
def year(y):
 office=13 if y<2018 else 7 if y==2018 else 6
 f=P/f'votacao_candidato_munzona_{y}_SC.csv'
 with f.open(encoding='latin1') as inp:
  rows=[r for r in csv.DictReader(inp,delimiter=';') if r['NR_TURNO']=='1' and int(r['CD_CARGO'])==office and (norm(r['NM_CANDIDATO'])=='BRUNO ANDRE DE SOUZA' or r['CD_MUNICIPIO']=='81051')]
 save(f'munzona-{y}.json',rows)
 with (P/f'detalhe_votacao_munzona_{y}_SC.csv').open(encoding='latin1') as inp:
  rows=[r for r in csv.DictReader(inp,delimiter=';') if r['NR_TURNO']=='1' and int(r['CD_CARGO'])==office and (y>=2018 or r['CD_MUNICIPIO']=='81051')]
 save(f'detalhes-{y}.json',rows)
 with (P/f'eleitorado_local_votacao_{y}_SC.csv').open(encoding='latin1') as inp:
  reader=csv.reader(inp,delimiter=';');h=next(reader);mi=h.index('CD_MUNICIPIO');ti=h.index('NR_TURNO');ui=h.index('SG_UF')
  rows=[dict(zip(h,r)) for r in reader if r[mi]=='81051' and r[ti]=='1' and r[ui]=='SC']
  # Drop telephone numbers: not needed for electoral geography.
  for r in rows:r.pop('NR_TELEFONE_LOCAL',None)
 save(f'cadastro-{y}.json',rows)
 with (P/f'votacao_secao_{y}_SC.csv').open(encoding='latin1') as inp:
  reader=csv.reader(inp,delimiter=';')
  if y==2012:
   rows=[{'zone':int(r[9]),'section':int(r[10]),'number':int(r[13]),'votes':int(r[14]),'local':None,'name':None,'address':None} for r in reader if r[7]=='81051' and r[3]=='1' and int(r[11])==office]
  else:
   h=next(reader); ix={k:h.index(k) for k in h};rows=[]
   for r in reader:
    if r[ix['CD_MUNICIPIO']]=='81051' and r[ix['NR_TURNO']]=='1' and int(r[ix['CD_CARGO']])==office:
     rows.append({'zone':int(r[ix['NR_ZONA']]),'section':int(r[ix['NR_SECAO']]),'number':int(r[ix['NR_VOTAVEL']]),'votes':int(r[ix['QT_VOTOS']]),'local':int(r[ix['NR_LOCAL_VOTACAO']]),'name':r[ix['NM_LOCAL_VOTACAO']],'address':r[ix['DS_LOCAL_VOTACAO_ENDERECO']]})
 save(f'votos-secao-{y}.json',rows)
 print(y,'done',len(rows),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(year,[2012,2016,2018,2022]))
