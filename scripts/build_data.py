"""Build an auditable electoral dataset. No inferred votes or geocoding."""
import csv,json,collections,unicodedata,hashlib,math,gzip
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'research'; I=P/'inputs'; D=ROOT/'dist'
def read(p):return json.loads(p.read_text() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+".gz").read_bytes()))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':')))
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.upper()) if unicodedata.category(c)!='Mn').strip()
def ni(v):return int(v) if v not in (None,'','-1','#NULO','#NE') else None
FIELDS=['votes','validVotes','nominalVotes','partyVotes','electorate','turnout','abstentions','blankVotes','nullVotes','subJudiceVotes','otherInvalidVotes','sections']
def empty():return {k:0 for k in FIELDS}
def add(a,b,fields=FIELDS):
 for k in fields:
  if b.get(k) is None:a[k]=None
  elif a.get(k) is not None:a[k]=a.get(k,0)+b[k]
def coord(v,lo,hi):
 try:n=float(v.replace(',','.'));return n if lo<n<hi else None
 except:return None
munconfig=read(P/'municipios-sc.json'); munbycode={r['cd']:r for r in munconfig}
checks=read(I/'candidaturas.json'); candidates={q['year']:q['matches'][0] for q in checks if q['matches']}
EL=[]; AUD=[]; ALLSEC=[]; snapshots={};sources=[]
for y in [2012,2016,2018,2022,2026]:
 c=candidates[y];num=int(c['NR_CANDIDATO']);off=int(c['CD_CARGO']);mun={};sourceDate=None
 if y<2026:
  mz=read(I/f'munzona-{y}.json');det=read(I/f'detalhes-{y}.json')
  for r in det:
   code=r['CD_MUNICIPIO'];m=mun.setdefault(code,{'id':code,'name':r['NM_MUNICIPIO'],'ibge':munbycode.get(code,{}).get('cdi'),**empty()})
   maps={'validVotes':'QT_TOTAL_VOTOS_VALIDOS','nominalVotes':'QT_VOTOS_NOMINAIS_VALIDOS','partyVotes':'QT_TOTAL_VOTOS_LEG_VALIDOS','electorate':'QT_APTOS','turnout':'QT_COMPARECIMENTO','abstentions':'QT_ABSTENCOES','blankVotes':'QT_VOTOS_BRANCOS','nullVotes':'QT_TOTAL_VOTOS_NULOS','subJudiceVotes':'QT_TOTAL_VOTOS_ANUL_SUBJUD','otherInvalidVotes':'QT_TOTAL_VOTOS_ANULADOS','sections':'QT_SECOES_PRINCIPAIS'}
   values={k:ni(r.get(v)) for k,v in maps.items()}
   values['validVotes']=values['nominalVotes']+values['partyVotes']
   add(m,values,list(maps))
  canrows=[r for r in mz if r['SQ_CANDIDATO']==c['SQ_CANDIDATO']]
  for r in canrows:mun[r['CD_MUNICIPIO']]['votes']+=int(r.get('QT_VOTOS_NOMINAIS_VALIDOS',r['QT_VOTOS_NOMINAIS']))
  sourceDate=canrows[0]['DT_GERACAO']; total=empty()
  for m in mun.values():add(total,m)
  officialTotal=total['votes']
  regrows=read(I/f'cadastro-{y}.json'); rawvotes=read(I/f'votos-secao-{y}.json')
  vr={}
  for r in mz:
   if r['CD_MUNICIPIO']=='81051':
    n=int(r['NR_CANDIDATO']);v=vr.setdefault(n,{'nominal':0,'valid':0,'dest':set()});v['nominal']+=int(r['QT_VOTOS_NOMINAIS']);v['valid']+=int(r.get('QT_VOTOS_NOMINAIS_VALIDOS',r['QT_VOTOS_NOMINAIS']));v['dest'].add(r.get('NM_TIPO_DESTINACAO_VOTOS','Válido'))
  partyrows=read(I/f'partidos-{y}.json');validparties={int(r['NR_PARTIDO']) for r in partyrows if y==2012 or int(r['QT_TOTAL_VOTOS_LEG_VALIDOS'])>0 or int(r['QT_VOTOS_NOMINAIS_VALIDOS'])>0}
  statuses={int(r['NR_CANDIDATO']):r for r in read(I/f'status-{y}.json')}
  secs={}
  for r in rawvotes:
   key=(r['zone'],r['section']);s=secs.setdefault(key,{'year':y,'zone':key[0],'section':key[1],'local':r['local'],'location':r['name'],'address':r['address'],**empty()});s['sections']=1
   n,q=r['number'],r['votes'];s['turnout']+=q
   if n==num:s['votes']+=q
   if n==95:s['blankVotes']+=q
   elif n==96:s['nullVotes']+=q
   elif n==97:s['subJudiceVotes']+=q
   elif n<95:
    if n in validparties:s['partyVotes']+=q
   elif statuses.get(n,{}).get('NM_TIPO_DESTINACAO_VOTOS')=='Válido (legenda)':s['partyVotes']+=q
   elif y==2012:
    if statuses.get(n,{}).get('DS_DETALHE_SITUACAO_CAND')=='DEFERIDO':s['nominalVotes']+=q
   elif n in vr and (vr[n]['valid']>0 or 'Válido' in vr[n]['dest'] or 'Válido (nominal)' in vr[n]['dest']):s['nominalVotes']+=q
  for s in secs.values():s['validVotes']=s['nominalVotes']+s['partyVotes'];s['electorate']=None;s['abstentions']=None
  status='Consolidado na base histórica'
 else:
  state=read(P/'2026-estado.json');offcan=next(v for a in state['carg'][0]['agr'] for p in a['par'] for v in p['cand'] if v['n']==str(num));officialTotal=int(offcan['vap']);sourceDate=state['dg']+' '+state['hg'];status='Totalização final · 100% das seções'
  def unified(j):
   cand=next(v for a in j['carg'][0]['agr'] for p in a['par'] for v in p['cand'] if v['n']==str(num));v=j['v'];e=j['e'];s=j['s']
   return {'votes':int(cand['vap']),'validVotes':int(v['vv']),'nominalVotes':int(v['vnom']),'partyVotes':int(v['vl']),'electorate':int(e['te']),'turnout':int(e['c']),'abstentions':int(e['a']),'blankVotes':int(v['vb']),'nullVotes':int(v['tvn']),'subJudiceVotes':int(v['vansj']),'otherInvalidVotes':int(v.get('van',0)),'sections':int(s['st'])}
  for mc in munconfig:
   j=read(P/'2026-municipios'/f"{mc['cd']}.json");assert j['and']=='f' and j['s']['st']==j['s']['ts'];mun[mc['cd']]={'id':mc['cd'],'name':mc['nm'],'ibge':mc['cdi'],**unified(j)}
  total=unified(state);assert sum(m['votes'] for m in mun.values())==officialTotal
  regrows=read(P/'cadastro-florianopolis-2026.json');bus=read(I/'boletins-2026.json');city=read(P/'2026-municipios/81051.json');parties=[p for a in city['carg'][0]['agr'] for p in a['par']];candstatuses={int(v['n']):v['dvt'] for p in parties for v in p['cand']};validc={int(v['n']) for p in parties for v in p['cand'] if v['dvt']=='Válido'};validp={int(p['n']) for p in parties if p['dvt']=='Válido (legenda)'};secs={}
  for bu in bus:
   key=(bu['zona'],bu['secao']);s={'year':y,'zone':key[0],'section':key[1],'local':bu['local'],'location':None,'address':None,**empty(),'turnout':bu['comparecimento'],'electorate':bu['aptosBu'],'abstentions':bu['aptosBu']-bu['comparecimento'],'sections':1,'source':bu['source'],'sha256':bu['sha256']}
   for v in bu['votos']:
    n,q,t=v['numero'],v['votos'],v['tipo']
    if t==1:
     if n==num:s['votes']+=q
     if n in validc:s['nominalVotes']+=q
     elif n not in candstatuses:s['nullVotes']+=q
     elif candstatuses[n]=='Anulado sub judice':s['subJudiceVotes']+=q
     else:s['otherInvalidVotes']+=q
    elif t==2:s['blankVotes']+=q
    elif t==3:s['nullVotes']+=q
    elif t==4:
     if v['partido'] in validp:s['partyVotes']+=q
     else:s['otherInvalidVotes']+=q
   s['validVotes']=s['nominalVotes']+s['partyVotes'];secs[key]=s
 reg={(int(r['NR_ZONA']),int(r['NR_SECAO'])):r for r in regrows};assert len(reg)==len(regrows)
 locreg=collections.defaultdict(list)
 for r in regrows:locreg[(int(r['NR_ZONA']),int(r['NR_LOCAL_VOTACAO']))].append(r)
 nbs={};locs={};missing=[];moved=[];den=empty();den['electorate']=0;den['abstentions']=0
 for key,s in secs.items():
  r=reg.get(key);match=r;reason=None
  if r and s['local'] is not None and int(r['NR_LOCAL_VOTACAO'])!=s['local']:
   alternatives=locreg.get((key[0],s['local']),[])
   match=alternatives[0] if alternatives and len({a['NM_BAIRRO'] for a in alternatives})==1 else None
   reason='Local do resultado diverge do cadastro retrospectivo; usado registro do local original no mesmo arquivo' if match else 'Local do resultado diverge do cadastro; bairro histórico não comprovado'
   moved.append({'year':y,'zone':key[0],'section':key[1],'resultLocation':s['local'],'registerLocation':int(r['NR_LOCAL_VOTACAO']),'votes':s['votes'],'resolution':reason})
  if not match:missing.append({'zone':key[0],'section':key[1],'votes':s['votes'],'reason':reason or 'Seção sem correspondência no cadastro do ano'})
  name=match['NM_BAIRRO'].strip() if match else 'Não classificado';name=name if name not in ('#NULO','#NE','') else 'Não classificado'
  local=s['local'] or (int(r['NR_LOCAL_VOTACAO']) if r else -1);lid=f'{key[0]}-{local}';s['local']=local;s['neighborhood']=name;s['locationId']=lid
  if s['location'] is None:s['location']=match['NM_LOCAL_VOTACAO'] if match else f'Local {local}'
  if s['address'] is None:s['address']=match['DS_ENDERECO'] if match else None
  nb=nbs.setdefault(name,{'id':norm(name),'name':name,**empty(),'locationIds':[]})
  lc=locs.setdefault(lid,{'id':lid,'zone':key[0],'code':local,'name':s['location'],'address':s['address'],'neighborhood':name,'latitude':coord(match['NR_LATITUDE'],-28,-27) if match else None,'longitude':coord(match['NR_LONGITUDE'],-49,-48) if match else None,'sectionNumbers':[],**empty()})
  assert lc['neighborhood']==name,(y,lid,'conflicting neighborhoods')
  lc['sectionNumbers'].append(key[1]);add(lc,s);add(nb,s);add(den,s)
  if lid not in nb['locationIds']:nb['locationIds'].append(lid)
  ALLSEC.append(s)
 for lc in locs.values():lc['sectionNumbers'].sort()
 city=mun['81051']; denominatorDelta=den['validVotes']-city['validVotes']; voteDelta=den['votes']-city['votes']
 assert voteDelta==0,(y,'section candidate reconciliation',voteDelta)
 # Percentages are withheld if old section returns cannot reproduce the updated valid-vote total.
 validDenominator=(denominatorDelta==0)
 if not validDenominator:
  for ob in list(nbs.values())+list(locs.values()):ob['validVotes']=None;ob['nominalVotes']=None;ob['partyVotes']=None
 for ob in list(nbs.values())+list(locs.values()):
  ob['validVotesVerified']=validDenominator
  if y<2026:
   ob['rawNullVotes']=ob['nullVotes'];ob['nullVotes']=None;ob['subJudiceVotes']=None;ob['otherInvalidVotes']=None
 for row in secs.values():
  row['validVotesVerified']=validDenominator
  if not validDenominator:
   row['rawReconstructedValidVotes']=row['validVotes'];row['validVotes']=None;row['nominalVotes']=None;row['partyVotes']=None
  if y<2026:
   row['source']=f'https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_{y}'+('_SC' if y>=2016 else '')+'.zip'
   row['rawNullVotes']=row['nullVotes'];row['nullVotes']=None;row['subJudiceVotes']=None;row['otherInvalidVotes']=None
 unclassified=nbs.get('Não classificado',{}).get('votes',0)
 snapshots[y]=locs
 audit={'year':y,'officialCandidateTotal':officialTotal,'sumMunicipalVotes':sum(m['votes'] for m in mun.values()),'municipalityDifference':sum(m['votes'] for m in mun.values())-officialTotal,'florianopolisOfficial':city['votes'],'sumNeighborhoodVotes':sum(n['votes'] for n in nbs.values()),'neighborhoodDifference':voteDelta,'unclassifiedVotes':unclassified,'classifiedVoteCoverage':100*(city['votes']-unclassified)/city['votes'],'sections':len(secs),'registeredSections':len(reg),'matchedSections':len(secs)-len(missing),'coordinatesLocations':sum(l['latitude'] is not None and l['longitude'] is not None for l in locs.values()),'locations':len(locs),'rawSectionValidVotes':den['validVotes'],'officialCityValidVotes':city['validVotes'],'validVoteDifference':denominatorDelta,'legacyTotalFieldDifference':sum(int(r['QT_TOTAL_VOTOS_VALIDOS']) for r in det if r['CD_MUNICIPIO']=='81051')-city['validVotes'] if y<2026 else 0,'neighborhoodPercentagesAvailable':validDenominator,'missing':missing,'relocated':moved,'registerGeneratedAt':regrows[0].get('DT_GERACAO','05/10/2026'),'sourceUpdatedAt':sourceDate}
 AUD.append(audit)
 el={'year':y,'date':c['DT_ELEICAO'],'office':c['DS_CARGO'].title(),'officeCode':off,'party':c['SG_PARTIDO'],'number':num,'candidateId':c['SQ_CANDIDATO'],'name':c['NM_CANDIDATO'],'birthDate':c['DT_NASCIMENTO'],'result':c['DS_SIT_TOT_TURNO'].capitalize().replace('qp','QP'),'territory':'Florianópolis' if off==13 else 'Santa Catarina','status':status,'sourceUpdatedAt':sourceDate,'totals':total,'municipalities':sorted(mun.values(),key=lambda m:-m['votes']),'neighborhoods':sorted(nbs.values(),key=lambda n:-n['votes']),'locations':sorted(locs.values(),key=lambda l:-l['votes']),'audit':audit}
 EL.append(el)
 print(y, 'votes',total['votes'],'city',city['votes'],'neighborhoods',len(nbs),'locations',len(locs),'classification',audit['classifiedVoteCoverage'],'denom diff',denominatorDelta,'moved',len(moved),flush=True)
changes=[]
for ya,yb in [(2012,2016),(2016,2018),(2018,2022),(2022,2026),(2018,2026)]:
 for lid in snapshots[ya].keys() & snapshots[yb].keys():
  a,b=snapshots[ya][lid],snapshots[yb][lid];diff={k:{'from':a[k],'to':b[k]} for k in ['name','address','neighborhood'] if a[k]!=b[k]}
  if diff:changes.append({'fromYear':ya,'toYear':yb,'locationId':lid,'changes':diff,'note':'Mesmo código de zona/local não comprova continuidade territorial. Diferença cadastral, não prova de mudança física.'})
for f in sorted(P.glob('*.source.json')):sources.append(read(f))
for title,url in [
 ('IBGE · malha municipal de Santa Catarina','https://servicodados.ibge.gov.br/api/v3/malhas/estados/42?formato=application/vnd.geo+json&qualidade=intermediaria&intrarregiao=municipio'),
 ('TSE · resultado estadual 2026','https://resultados.tse.jus.br/oficial/ele2026/6259/dados/sc/sc-c0007-e006259-u.json'),
 ('TSE · cadastro eleitoral 2026','https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip'),
 ('TSE · configuração de municípios e códigos IBGE','https://resultados.tse.jus.br/oficial/ele2026/6259/config/mun-e006259-cm.json'),
 ('TRE-SC · candidato por seção 2022','https://apps.tre-sc.jus.br/site/fileadmin/arquivos/eleicoes/eleicoes2022/resultados_turno_1/candidato_secao/relatorio_secao_deferidos/dep_federal/df_3020.pdf')]:sources.append({'title':title,'url':url,'accessedAt':'2026-10-07'})
# Operational, explicit geography; no claim that this is every legal definition of the metro area.
greater=['ÁGUAS MORNAS','ANTÔNIO CARLOS','BIGUAÇU','FLORIANÓPOLIS','GOVERNADOR CELSO RAMOS','PALHOÇA','SANTO AMARO DA IMPERATRIZ','SÃO JOSÉ','SÃO PEDRO DE ALCÂNTARA']
data={'asOf':'2026-10-07','name':'Bruno André de Souza','elections':EL,'candidatureSearch':checks,'sources':sources,'greaterFlorianopolis':greater,'geography':read(P/'sc-municipios.geojson'),'locationChanges':changes}
save(D/'base-tratada.json',data);(D/'data.js').write_text('window.ELECTION_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
save(D/'auditoria.json',AUD);save(D/'mudancas-cadastrais.json',changes);save(D/'secoes.json',ALLSEC);save(D/'fontes.json',sources)
for level in ['municipalities','neighborhoods','locations']:
 rows=[]
 for e in EL:
  for r in e[level]:rows.append({'ano':e['year'],'cargo':e['office'],'territorio':r['name'],'votos':r['votes'],'votos_validos':r['validVotes'],'percentual_validos':round(r['votes']/r['validVotes']*100,8) if r['validVotes'] else None,'contribuicao_total_candidato':round(r['votes']/e['totals']['votes']*100,8),'bairro':r.get('neighborhood'),'zona':r.get('zone'),'local':r.get('code'),'endereco':r.get('address'),'latitude':r.get('latitude'),'longitude':r.get('longitude')})
 with (D/(level+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
