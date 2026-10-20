#!/usr/bin/env python3
"""Build deterministic offline course data; every quiz prompt written in questions.tsv."""
import json,re,datetime,unicodedata,collections,hashlib,pathlib
base=pathlib.Path(__file__).resolve().parents[1]
vert=pathlib.Path('/mnt/data/_Edital_Verticalizado_Miriam_.txt')
subjects={'P':'Língua Portuguesa','R':'Raciocínio Lógico','I':'Noções de Informática','G':'Conhecimentos Gerais','L':'Legislação','E':'Conhecimentos Específicos'}
weights={'P':4,'R':3,'I':3,'G':3,'L':3,'E':4}
source=vert.read_text() if vert.exists() else (base/'scripts/verticalizado-extraido.txt').read_text()
(base/'scripts/verticalizado-extraido.txt').write_text(source)
name_to_code=['P','R','I','G','L','E']
parts=re.split(r'\b0([1-6]) / (?:LÍNGUA PORTUGUESA|RACIOCÍNIO LÓGICO|NOÇÕES DE INFORMÁTICA|CONHECIMENTOS GERAIS|LEGISLAÇÃO|CONHECIMENTOS ESPECÍFICOS)',source)
topics=[]
for i in range(1,len(parts),2):
  try: subject=name_to_code[int(parts[i])-1]
  except (ValueError,IndexError):continue
  body=parts[i+1]
  for m in re.finditer(r'^\s{2,}([^\n]+?)\s{2,}(P[123])\s+___\s*/\s*___\s*$',body,re.M):
    label=m.group(1).strip()
    if label.startswith('SUBTÓPICO'):continue
    topics.append({'id':f'{subject}-{sum(t["subject"]==subject for t in topics)+1:03d}', 'subject':subject, 'name':label,'priority':m.group(2),'kind':'roteiro didático'})
assert len(topics)>200,('verticalized parse incomplete',len(topics))
raw=[]
for i,line in enumerate((base/'scripts/questions.tsv').read_text().splitlines()):
  if not line.strip():continue
  a=line.split('|');assert len(a)==8,(i+1,len(a))
  subj,stem,right,w1,w2,w3,expl,tag=a
  assert subj in subjects and len(stem)>8 and len(expl)>20
  # Correct answer permutation, stable and balanced across dataset
  index=len([q for q in raw if q['subject']==subj])
  correct_at=(index*3 + ord(subj))%4
  others=[w1.strip(),w2.strip(),w3.strip()]
  options=others[:];options.insert(correct_at,right.strip())
  raw.append({'id':f'Q-{subj}-{index+1:03d}','subject':subj,'topic':tag.strip(),'stem':stem.strip(),'options':options,'answer':correct_at,'explanation':expl.strip(),'origin':'Autoral — estilo IBGP (não é questão oficial da banca)','difficulty':'intermediária','source':'Conteúdo programático e referências indicadas na aula'})
questions=raw
assert len(questions)>=120
qBySub={s:[q['id'] for q in questions if q['subject']==s] for s in subjects}
assert all(len(x)>=20 for x in qBySub.values())
rows=[line.split('|') for line in (base/'scripts/sessions.tsv').read_text().splitlines() if line.strip()]
assert len(rows)==47
assert all(len(row)==6 for row in rows)
date=datetime.date(2026,10,20)
dates=[]
while date<=datetime.date(2026,12,12):
 if date.weekday()!=6:dates.append(date.isoformat())
 date+=datetime.timedelta(days=1)
assert len(dates)==47
simN=0;sims=[];days=[]
for i,(date,row) in enumerate(zip(dates,rows)):
  sub,title,text,example,trap,source=row
  d={'id':f'D{i+1:02d}','date':date,'subject':sub,'title':title,'theory':text,'example':example,'trap':trap,'source':source,'phase':('Fundamentos' if date<='2026-11-14' else 'Consolidação' if date<='2026-11-28' else 'Reta final'), 'duration':180 if sub=='S' else 120 if sub=='F' else 150, 'reviews':[],'qids':[], 'topicIds':[]}
  if sub=='S':
    simN+=1;d['simId']=f'SIM-{simN}'
    sq=[]
    for s in subjects:
      sq.extend(qBySub[s][(simN-1)*5:simN*5])
    assert len(sq)==30
    sims.append({'id':f'SIM-{simN}', 'dayId':d['id'],'date':date,'title':title,'duration':10800,'qids':sq})
  else:
    # 8 questions on theory days; 4 on final rest-focused day
    count=4 if sub=='F' else 8
    # Weights to the day subject; 4 from same category, four alternated across previously studied subjects
    primary='E' if sub=='F' else sub
    ids=qBySub[primary]
    for j in range(min(4,count)):
      d['qids'].append(ids[(i*3+j)%len(ids)])
    if count>4:
      support=[s for s in subjects if s!=primary]
      for j in range(count-4):
       s=support[(i+j)%len(support)]; ids=qBySub[s]
       d['qids'].append(ids[(i*2+j)%len(ids)])
  days.append(d)
assert simN==4
# Optional precise extracts from attached municipal law PDFs.
normative=json.loads((base/'scripts/normative_readings.json').read_text()) if (base/'scripts/normative_readings.json').exists() else {}
for day in days:
 if day['id'] in normative: day['reading']=normative[day['id']]
# Schedule spaced reviews at +1,3,7,14 calendar days, shift Sunday reviews to next study day.
for i,d in enumerate(days):
 if d['subject']=='S':continue
 for delta in [1,3,7,14]:
  k=next((k for k in range(i-1,-1,-1) if (datetime.date.fromisoformat(d['date'])-datetime.date.fromisoformat(days[k]['date'])).days>=delta),None)
  if k is not None and days[k]['subject'] not in ['S','F'] and days[k]['id'] not in d['reviews']:
   d['reviews'].append(days[k]['id'])
 d['reviews']=d['reviews'][-3:]
# Link topics to nearest matching daily lesson; links are suggested study routes, not certification of content coverage.
def norm(s):
 s=unicodedata.normalize('NFKD',s.lower());return ''.join(x for x in s if not unicodedata.combining(x))
def words(s):
 return set(x for x in re.findall('[a-z]{4,}',norm(s)) if x not in {'para','pela','pelos','sobre','entre','como','pela','municipio','noções','nocões','conjunto','conceitos','aspectos','formas','outros','aplicados','relativos'})
bySub=collections.defaultdict(list)
for d in days:
 if d['subject'] in subjects:bySub[d['subject']].append(d)
for t in topics:
 pool=bySub[t['subject']]
 tw=words(t['name'])
 def score(d):
  title=words(d['title']);body=words(d['theory']+' '+d['source']);both=len(tw&title)*4+len(tw&body)
  return both - .002*int(d['id'][1:])
 best=max(pool,key=score)
 best['topicIds'].append(t['id'])
 t['routeDay']=best['id']
 # Verified coverage requires specific explanation in the lesson, not mere navigation association
 t['verifiedLesson']=(len(tw&words(best['theory']))>=min(2,len(tw)) and score(best)>=2)
 # Link relevant question only when subject and topic stem/tag have lexical signal
 qq=[q['id'] for q in questions if q['subject']==t['subject'] and (len(tw&words(q['topic']))>=min(1,len(tw)) or len(tw&words(q['stem']))>=min(2,len(tw)))]
 t['questionIds']=qq[:8]
 t['coverageStatus']='vinculação preliminar — requer auditoria pedagógica' if t['verifiedLesson'] else 'não validado pedagogicamente'
# Flashcards prewritten from question statements and authored detailed rationales
flashcards=[]
for q in questions:
 flashcards.append({'id':'C-'+q['id'],'subject':q['subject'],'topic':q['topic'],'prompt':q['stem'],'answer':q['options'][q['answer']],'explanation':q['explanation'],'questionId':q['id'], 'priority':'P1'})
sourceLinks=[
 {'name':'Edital nº 02/2026, consolidado','url':'./public/fontes/edital-02-2026.pdf','kind':'anexo fornecido'},
 {'name':'Retificação nº 01','url':'./public/fontes/retificacao-01.pdf','kind':'anexo fornecido'},
 {'name':'Anexo I — cargos, requisitos e vagas','url':'./public/fontes/anexo-i.pdf','kind':'anexo fornecido'},
 {'name':'Anexo III — prova e pesos','url':'./public/fontes/anexo-iii.pdf','kind':'anexo fornecido'},
 {'name':'Anexo IV — conteúdo programático retificado','url':'./public/fontes/anexo-iv-retificado.pdf','kind':'anexo fornecido'},
 {'name':'Edital verticalizado Miriam','url':'./public/fontes/edital-verticalizado.pdf','kind':'material organizacional'},
 {'name':'Código Tributário Municipal — Lei 4.012/2006','url':'./public/fontes/codigo-tributario-municipal-lei-4012-2006.pdf','kind':'PDF fornecido; verificar alterações'},
 {'name':'Estatuto dos servidores — Lei 5.038/2014','url':'./public/fontes/estatuto-servidores-lei-5038-2014.pdf','kind':'PDF fornecido; verificar alterações'},
 {'name':'Lei Orgânica de São João del-Rei','url':'./public/fontes/lei-organica-sao-joao-del-rei.pdf','kind':'PDF fornecido; verificar alterações'},
 {'name':'Câmara Municipal — Lei 4.012 e alterações','url':'https://www.camarasaojoaodelrei.mg.gov.br/texto_lei/1342','kind':'fonte oficial externa'},
 {'name':'ALMG — Decreto Estadual 45.969/2012','url':'https://www.almg.gov.br/legislacao-mineira/texto/DEC/45969/2012/atualizado','kind':'fonte oficial externa'},
 {'name':'Constituição Federal — Planalto','url':'https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm','kind':'fonte federal externa'},
 {'name':'Código Tributário Nacional — Planalto','url':'https://www.planalto.gov.br/ccivil_03/leis/l5172compilado.htm','kind':'fonte federal externa'},
 {'name':'Lei 14.133/2021 — Planalto','url':'https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm','kind':'fonte federal externa'},
 {'name':'Lei 13.146/2015 — Planalto','url':'https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm','kind':'fonte federal externa'},
 {'name':'Lei 12.527/2011 — Planalto','url':'https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12527.htm','kind':'fonte federal externa'},
 {'name':'Lei 4.320/1964 — Planalto','url':'https://www.planalto.gov.br/ccivil_03/leis/l4320.htm','kind':'fonte federal externa'},
 {'name':'Banco de provas — portal IBGP','url':'https://www.ibgpconcursos.com.br/','kind':'fonte para pesquisa; questões deste curso são autorais'}
]
course={'version':1,'student':'Miriam','exam':{'job':'325 — Agente Fiscal de Tributos','city':'São João del-Rei/MG','board':'IBGP','number':'02/2026','date':'2026-12-13','start':'14:45','end':'17:45','questions':30,'points':100},'subjects':subjects,'weights':weights,'days':days,'sims':sims,'topics':topics,'questions':questions,'flashcards':flashcards,'sources':sourceLinks}
(base/'src/data/course.js').write_text('/* Gerado de scripts/sessions.tsv e scripts/questions.tsv. */\nexport const course = '+json.dumps(course,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
(base/'scripts/course-data.json').write_text(json.dumps(course,ensure_ascii=False,indent=2))
print('days',len(days),'sim',len(sims),'questions',len(questions),'cards',len(flashcards),'official didactic topics',len(topics),'verifiedLesson',sum(t['verifiedLesson'] for t in topics))
print(collections.Counter(t['subject'] for t in topics))
