import csv,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'research';I=P/'inputs'
for y in [2012,2016,2018,2022]:
 off=str(13 if y<2018 else 7 if y==2018 else 6)
 with (P/f'votacao_partido_munzona_{y}_SC.csv').open(encoding='latin1') as f: rows=[r for r in csv.DictReader(f,delimiter=';') if r['NR_TURNO']=='1' and r['CD_CARGO']==off and r['CD_MUNICIPIO']=='81051']
 (I/f'partidos-{y}.json').write_text(json.dumps(rows,ensure_ascii=False))
 with (P/f'consulta_cand_{y}_SC.csv').open(encoding='latin1') as f: rows=[{k:r.get(k) for k in ['NR_CANDIDATO','DS_DETALHE_SITUACAO_CAND','NM_TIPO_DESTINACAO_VOTOS','DS_SITUACAO_CANDIDATURA']} for r in csv.DictReader(f,delimiter=';') if r['CD_CARGO']==off and r['NR_TURNO']=='1' and (y>=2018 or r['NM_UE']=='FLORIANÓPOLIS')]
 (I/f'status-{y}.json').write_text(json.dumps(rows,ensure_ascii=False))
