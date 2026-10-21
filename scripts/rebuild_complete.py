"""Reorganização editorial das 47 sessões com guias autorais, exercícios rastreáveis e auditoria."""
from aulas_aprofundadas import GUIDES
from casos_resolvidos import PRACTICE
from pathlib import Path
from collections import defaultdict,Counter
import json, re, csv, datetime, hashlib, random, unicodedata
BASE=Path(__file__).resolve().parents[1]
original=json.loads((BASE/'scripts/course-data-original.json').read_text())
D=original
S=D['subjects']; subjects='PRIGLE'
byday={d['id']:d for d in D['days']}
byorig={q['id']:q for q in D['questions']}

# Explicitly curated source-to-session map: no cross-discipline daily exercises.
OLD_ASSIGN={
'D01':'E-001 E-002 E-003 E-004', 'D02':'L-010 L-011 L-023', 'D03':'P-001 P-002 P-003 P-017 P-018 P-019 P-020 P-021',
'D04':'E-022 E-023', 'D05':'R-001 R-002 R-003 R-011 R-014 R-022','D06':'L-001 L-002 L-003 L-022',
'D07':'I-001 I-002 I-023','D08':'E-002 E-003 E-004','D09':'L-004 L-005','D10':'G-001 G-002 G-003 G-004 G-005 G-006 G-007 G-009 G-014',
'D11':'E-005 E-006','D12':'P-004 P-005 P-006 P-022 P-023','D13':'E-012 E-013 E-024','D14':'L-012 L-023',
'D15':'I-003 I-004 I-012 I-013 I-014 I-017','D17':'R-004 R-012 R-013 R-019','D18':'E-021',
'D19':'L-007 L-008','D20':'E-015','D21':'P-008 P-014 P-015 P-016','D22':'L-009 L-022',
'D23':'I-005 I-006 I-007 I-008 I-009','D24':'E-014','D25':'L-013 L-014','D26':'R-005 R-006 R-007 R-010 R-015 R-016 R-017 R-018 R-021 R-023 R-024',
'D27':'E-007','D28':'L-006 L-021 L-024','D30':'E-008 E-009 E-010','D31':'I-010 I-011 I-021 I-024',
'D32':'E-017 E-018 E-019','D33':'P-007 P-012 P-013','D34':'L-018 L-019 L-020',
'D35':'R-008 R-009 R-020','D36':'E-020','D37':'L-023','D39':'E-006 E-007',
'D40':'I-012 I-013 I-014 I-015 I-016 I-017 I-018 I-019 I-020 I-022',
'D41':'G-008 G-010 G-011 G-012 G-013 G-015 G-016 G-017 G-018 G-019 G-020 G-021 G-022 G-023 G-024',
'D42':'E-011','D44':'L-015 L-016 L-017','D45':'E-016 E-003 E-004','D46':'P-009 P-010 P-011 P-024',
'D47':'E-001 E-010 L-006 R-002 P-004'
}
# Topic route derived from editorial groups (published checklist names are not proof of in-depth coverage).
TOPIC_ROUTE={
'P':[(1,9,'D03'),(10,11,'D46'),(12,22,'D21'),(23,28,'D12'),(29,32,'D46'),(33,35,'D33'),(36,36,'D46')],
'R':[(1,7,'D05'),(8,21,'D17'),(22,38,'D26'),(39,41,'D35')],
'I':[(1,17,'D07'),(18,22,'D15'),(23,26,'D31'),(27,29,'D23'),(30,38,'D31'),(39,47,'D40'),(48,49,'D31'),(50,52,'D40'),(53,56,'D15'),(57,63,'D40')],
'G':[(1,14,'D10'),(15,41,'D41')],
'L':[(1,1,'D02'),(2,2,'D06'),(3,4,'D25'),(5,5,'D09'),(6,14,'D19'),(15,21,'D28'),(22,23,'D34'),(24,25,'D44')],
'E':[(1,4,'D04'),(5,5,'D18'),(6,6,'D36'),(7,7,'D04'),(8,15,'D01'),(16,17,'D08'),(18,18,'D11'),(19,19,'D27'),(20,20,'D30'),(21,21,'D39'),(22,22,'D32'),(23,23,'D20'),(24,24,'D13'),(25,25,'D24'),(26,27,'D45'),(28,28,'D01'),(29,31,'D13'),(32,33,'D42'),(34,37,'D47')]
}
for d in D['days']:
 d['topicIds']=[]
for t in D['topics']:
 s,num=t['id'].split('-'); num=int(num)
 matches=[route for a,b,route in TOPIC_ROUTE[s] if a<=num<=b]
 assert len(matches)==1,(t['id'],matches)
 day=byday[matches[0]];day['topicIds'].append(t['id']);t['routeDay']=day['id']
 t['verifiedLesson']=False  # subject index is *not* equivalent to substantive proof of coverage
 t['coverageStatus']='roteiro pedagógico; confira exposição e fontes antes de marcar como dominado'
 t['questionIds']=[]

# Some broad statutory topics return on later fixed dates: make the reference
# visible on those days, without pretending that a single official topic
# was exhausted the first time it was studied.
for repeatday,topid in {'D14':'L-001','D22':'L-002','D37':'L-001'}.items():
    byday[repeatday]['topicIds'].append(topid)
    item=next(t for t in D['topics'] if t['id']==topid)
    item.setdefault('secondaryDays',[]).append(repeatday)

# Turn 4-5 authored conceptual sections into short, same-day discriminative exercises.
def getsections(markdown):
 sections=[]
 for x in re.split(r'(?=^##\s)',markdown,flags=re.M):
  a=x.strip()
  if not a.startswith('## '):continue
  pieces=a.split('\n',1)
  if len(pieces)<2:continue
  head=pieces[0][3:].strip(); text=pieces[1].strip()
  sentences=re.split(r'(?<=[.!?])\s+',text)
  # Learning anchors are authored factual paragraphs rather than arbitrary document headings.
  anchor=' '.join(sentences[:2]).replace('**','').strip()
  sections.append((head,anchor,text))
 return sections

# Map each study theme to 8+ fixed exercises (authored cases, selected topical questions,
# and recall discrimination based on *that day's* authored lesson). Last day uses case + revision.
new_questions=[]
for line_no,line in enumerate((BASE/'scripts/questoes_casos.txt').read_text().splitlines(),1):
 if not line.strip():continue
 fields=line.split('|')
 assert len(fields)==8,(line_no,len(fields))
 did,topic,stem,right,*rest=fields
 wrong=rest[:3];reason=rest[3]
 assert did in GUIDES and len(set([right,*wrong]))==4,(did,line_no)
 ix=len(new_questions)+1
 choices=[right,*wrong]
 rand=random.Random(2026+ix*37);rand.shuffle(choices)
 ans=choices.index(right)
 feedback=' '.join(f"{'ABCD'[i]}) {'Correta' if i==ans else 'Incorreta'} — “{opt}”: {reason if i==ans else 'Essa alternativa desloca o enquadramento do fato descrito. '+reason}" for i,opt in enumerate(choices))
 new_questions.append({'id':f'N-{did}-{ix:03d}', 'subject':byday[did]['subject'] if did!='D47' else 'E','topic':topic,
    'stem':stem,'options':choices,'answer':ans, 'explanation':reason+' '+feedback,
    'origin':'Autoral — questão aplicada elaborada para esta aula (não é prova oficial IBGP)', 'difficulty':'intermediária',
    'source':byday[did]['source'],'dayId':did,'kind':'caso'})
assert len(new_questions)==89
new_byday=defaultdict(list)
for q in new_questions:new_byday[q['dayId']].append(q['id'])

# Each recall question makes a specific distinction among 4 concepts explicitly explained in the lesson.
# Such items are labeled "fixação" rather than represented as former IBGP questions.
def terms_from_guide(txt):
 """Extract short self-contained clauses; avoid exposing answers or gibberish fragments."""
 ret=[]
 for h,anchor,body in getsections(txt):
  for term in re.findall(r'\*\*([^*]{3,63})\*\*',body):
   term=term.strip(' .,;:')
   if len(term)<4 or len(term)>48 or len(term.split())>5:continue
   if not re.match(r'^[A-ZÀ-Ýa-zà-ÿ]',term):continue
   if any(x in term.casefold() for x in ['não é','não se','separ','exemplo','treino','atenção','como','caso','questões','regra geral']):continue
   if any(ch in term for ch in [';',':','\n','[',']','(',')','→','/','=']):continue
   if any(term.casefold()==t[0].casefold() for t in ret):continue
   sentences=re.split(r'(?<=[.!?])\s+',body.replace('**',''))
   clause=None
   for sentence in sentences:
    for part in re.split(r'[;]',sentence):
     part=part.strip(' .')
     if re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',part,flags=re.I) and len(part)>33:
      clause=part;break
    if clause:break
   if not clause:continue
   gloss=re.sub(r'(?<!\w)'+re.escape(term)+r'(?!\w)','[conceito]',clause,count=1,flags=re.I).strip()
   if not (30<=len(gloss)<=210) or gloss.count('[conceito]')!=1:continue
   if re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',gloss,flags=re.I):continue
   ret.append((term,gloss,h))
 return ret

for day in D['days']:
 did=day['id'];subject=day['subject'];day['qids']=[]
 if subject=='S':continue
 day['deepTheory']='## Ponto de partida — leia antes de responder\n'+day['theory']+'\n\n'+GUIDES[did]+'\n\n'+PRACTICE[did]+'\n\n## Aplicação e retomada final\n'+day['example']+'\n\n**Atenção:** '+day['trap']+'\n\n**Fontes primárias:** '+day['source']+'.'
 day['editorialStatus']='Material editorial específico + exercícios fixos; revisão jurídica final de alterações ainda recomendada'
 # First relevant authored cases; then matched old items, finally enough lesson-grounded concept distinctions.
 if did=='D47':
  day['qids'].extend(new_byday[did])
  desired=8
 else:
  day['qids'].extend(new_byday[did])
  old=[f'Q-{tag}' for tag in OLD_ASSIGN.get(did,'').split()]
  old=[qid for qid in old if qid in byorig and byorig[qid]['subject']==subject]
  for qid in old:
   if len(day['qids'])>=5:break  # guarantees most exercises are not old bank repeats
   if qid not in day['qids']:day['qids'].append(qid)
  desired=8
 if len(day['qids'])<desired:
  concepts=terms_from_guide(GUIDES[did]);
  # The other answers are topic concepts, not unrelated disciplinary content.
  seen=[]
  for term,gloss,h in concepts:
   if len(day['qids'])>=desired:break
   # Distinct distractors, including from additional valid technical concepts taught that day.
   peers=[t for t,g,k in concepts if t!=term and t.casefold()!=term.casefold()]
   candidates=[]
   for other in peers:
    if other not in candidates and other!=term:candidates.append(other)
   if len(candidates)<3:continue
   distractors=candidates[(len(seen)*2)%len(candidates):]+candidates[:(len(seen)*2)%len(candidates)]
   choices=[term,*distractors[:3]]
   if len(set(choices))<4:continue
   rand=random.Random(int(did[1:])*500+len(seen));rand.shuffle(choices)
   ans=choices.index(term)
   # Description is directly excerpted from today's original instructional section.
   stem=f'Leia a descrição estudada na aula: “{gloss}”. A que conceito essa descrição se refere mais diretamente?'
   why=f'A passagem está na seção «{h}» e define ou exemplifica {term}. As demais opções designam outros conceitos abordados na aula e não correspondem à descrição específica apresentada.'
   details=' '.join(f"{'ABCD'[j]}) {('Correta' if j==ans else 'Incorreta')}: {o} — "+(f'corresponde à descrição da seção {h}.' if j==ans else f'naquela seção, o elemento descrito é {term}, e não {o}.') for j,o in enumerate(choices))
   q={'id':f'F-{did}-{len(seen)+1:02d}','subject':('E' if subject=='F' else subject),'topic':h,
     'stem':stem,'options':choices,'answer':ans,'explanation':why+' '+details,'origin':'Autoral — fixação de conceito deste dia (não é questão real IBGP)',
     'difficulty':'fundamental','source':day['source'],'dayId':did,'kind':'fixacao'}
   new_questions.append(q);day['qids'].append(q['id']);seen.append(term)
 # If material offers fewer terminology anchors, add original SAME-DAY questions not yet selected, not cross-discipline.
 if len(day['qids'])<desired and subject!='F':
  for qid in [f'Q-{tag}' for tag in OLD_ASSIGN.get(did,'').split()]:
   if len(day['qids'])>=desired:break
   if qid in byorig and byorig[qid]['subject']==subject and qid not in day['qids']:day['qids'].append(qid)
 if len(day['qids'])<desired:
  sections=getsections(GUIDES[did]);
  # Final fallback: factual comprehension of a SPECIFIC authored paragraph of today's lesson.
  # All alternatives are headings from today's text; none introduces an extraneous discipline.
  passnum=0
  while len(day['qids'])<desired and passnum<20:
   ind=passnum%len(sections);h,anchor,body=sections[ind]
   sentences=[x.strip() for x in re.split(r'(?<=[.!?])\s+',body.replace('**','')) if len(x.strip())>=65]
   excerpt=sentences[min(passnum//len(sections),len(sentences)-1)] if sentences else anchor
   titleWords=[x for x in re.findall(r'[A-Za-zÀ-ÿ]{5,}',h) if x.lower() not in ['sobre','entre','questões','entender']]
   for term in titleWords[:2]:
    excerpt=re.sub(r'(?i)\b'+re.escape(term)+r'\b','[tema]',excerpt)
   heads=[x[0] for x in sections]
   candidates=[x for x in heads if x!=h]
   if len(candidates)<3:break
   choices=[h,*candidates[(passnum)%len(candidates):],*candidates[:(passnum)%len(candidates)]]
   choices=choices[:4];rand=random.Random(5132+int(did[1:])*97+passnum);rand.shuffle(choices)
   ans=choices.index(h)
   q={'id':f'R-{did}-{passnum+1:02d}','subject':('E' if subject=='F' else subject),'topic':h,
      'stem':f'Na teoria da sessão de hoje, o trecho “{excerpt}” desenvolve mais diretamente qual dos temas abaixo?',
      'options':choices,'answer':ans,
      'explanation':f'O trecho foi explicado em «{h}»: {anchor} '+ ' '.join(f"{'ABCD'[j]}) "+ ('Correta: corresponde ao tema do trecho.' if j==ans else f'Incorreta: «{o}» é outra seção, não o objeto do trecho destacado.') for j,o in enumerate(choices)),
      'origin':'Autoral — recuperação ativa da leitura desta aula (não é prova IBGP)','difficulty':'fundamental','source':day['source'],'dayId':did,'kind':'leitura'}
   new_questions.append(q);day['qids'].append(q['id']);passnum+=1
 if len(day['qids'])<desired:
  raise RuntimeError(f'{did} has only {len(day["qids"])} exercises (expected 8). Authored concepts: {len(terms_from_guide(GUIDES[did]))}')
 assert len(day['qids'])==desired
 day['duration']=150 if subject!='F' else 120
 day['timePlan']={'teoria':87 if subject!='F' else 55,'questoes':46 if subject!='F' else 35,'revisao':17 if subject!='F' else 30}

# Do not use the old generated flashcard metadata as a proxy for coverage.
all_questions=D['questions']+new_questions
qmap={q['id']:q for q in all_questions}
for d in D['days']:
 if d['subject']=='S':continue
 for qid in d['qids']:
  q=qmap[qid]
  assert q['subject']==d['subject'] or (d['subject']=='F'),(d['id'],qid,q['subject'])
  assert len(q['options'])==4 and len(set(q['options']))==4
  # All non-original cases are associated with exactly this day in the published course.
  assert not (q.get('dayId') and q['dayId']!=d['id'])
D['questions']=all_questions
D['flashcards']=[{'id':'C-'+q['id'],'subject':q['subject'],'topic':q['topic'],'prompt':q['stem'],
  'answer':q['options'][q['answer']],'explanation':q['explanation'],'questionId':q['id'],'priority':'P1'} for q in all_questions]
D['version']=2
D['buildInfo']={'author':'Material didático e banco autoral produzidos para Miriam Estudos', 'editorial':'Material diário escrito para as 43 sessões com teoria; 4 simulados fixos. Guias de leitura ainda exigem verificação legal consolidada e revisão humana do conjunto completo.',
 'realIBGPQuestions':0,'freshCases':89,'reminders':'Sem execução automática remota: atualização do GitHub requer envio de arquivos.'}
# Each topic is tracked to a date; old claims of "verified" based on lexical overlap were removed.
for t in D['topics']:
 day=byday[t['routeDay']]
 t['questionIds']=[qid for qid in day['qids'] if qmap[qid]['subject']==t['subject'] and (t['name'].casefold() in qmap[qid]['topic'].casefold() or qmap[qid]['topic'].casefold() in t['name'].casefold())][:4]
# Prevent the obsolete original question distribution from being regenerated during deploy.
(BASE/'scripts/course-data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
(BASE/'src/data/course.js').write_text('/* Matriz fixa Miriam Estudos: edição 2026.10 (edição autoral). */\nexport const course = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('Saved',len(D['days']),'sessions',len(D['questions']),'questions',len(D['flashcards']),'cards',len(D['topics']),'topics')
print('new question types:',Counter(q.get('kind','original') for q in D['questions']))
print('minimum theory words',min((len(d['deepTheory'].split()),d['id']) for d in D['days'] if d['subject']!='S'))
