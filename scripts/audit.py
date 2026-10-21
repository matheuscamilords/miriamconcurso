#!/usr/bin/env python3
"""Auditoria reproduzível da integridade (não constitui revisão jurídico-pedagógica)."""
from pathlib import Path
from collections import Counter,defaultdict
import json,csv,re,datetime,sys
root=Path(__file__).resolve().parents[1]
c=json.loads((root/'scripts/course-data.json').read_text(encoding='utf-8'))
issues=[];warnings=[]
def must(ok,msg):
 if not ok:issues.append(msg)
D=c['days'];Q=c['questions'];T=c['topics'];S=c['sims'];byq={x['id']:x for x in Q};byd={x['id']:x for x in D};sub=set(c['subjects']);bytopic={x['id']:x for x in T}
weights=c['weights'];daycounts=Counter();kinds=Counter(q.get('kind','original') for q in Q)
must(len(D)==47,'Cronograma não possui 47 sessões')
must(len(Q)==len(byq),'IDs de questões repetidos')
must(len(T)==len(bytopic)==243,'Edital verticalizado sem os 243 subtópicos')
must(len(S)==4,'Não há exatamente 4 simulados')
must(len(c['flashcards'])==len(Q),'Flashcards não correspondem ao banco')
expected=[(datetime.date(2026,10,20)+datetime.timedelta(days=n)).isoformat() for n in range(54) if (datetime.date(2026,10,20)+datetime.timedelta(days=n)).weekday()!=6]
must([x['date'] for x in D]==expected,'Calendário não é a sequência esperada sem domingos (20/10-12/12)')
for d in D:
 kind=d['subject']; did=d['id'];daycounts[kind]+=1
 if kind=='S':
  must(d.get('simId') in {s['id'] for s in S},f'{did}: simulado não identificado')
  continue
 must(isinstance(d.get('deepTheory'),str) and len(d['deepTheory'].split())>=450,f'{did}: aula sem explicação individualizada de pelo menos 450 palavras')
 must(len(d.get('qids',[]))==8,f'{did}: precisa ter exatamente 8 exercícios fixos')
 must(len(set(d.get('qids',[])))==len(d.get('qids',[])),f'{did}: questão repetida dentro do dia')
 must(bool(d.get('topicIds')),f'{did}: sem tópicos de referência')
 must(all(x in bytopic for x in d.get('topicIds',[])),f'{did}: tópico não indexado')
 must(d.get('timePlan',{}).get('teoria',0)>0,f'{did}: sem planejamento em minutos')
 must(d['duration'] in (120,150),f'{did}: duração errada')
 case_count=0
 for qid in d.get('qids',[]):
  if qid not in byq:issues.append(f'{did}: questão {qid} ausente');continue
  q=byq[qid];case_count+=q.get('kind')=='caso'
  must(kind=='F' or q['subject']==kind,f'{did}: questão de outra matéria ({qid})')
  must(not q.get('dayId') or q['dayId']==did,f'{did}: {qid} foi escrito para outra data')
 must(case_count>=2,f'{did}: menos de duas questões aplicadas próprias')
 if len(d.get('topicIds',[]))>12:
  warnings.append(f'{did}: {len(d["topicIds"])} referências de subtópicos numa única aula; há risco de abordagem insuficiente.')
for q in Q:
 qid=q['id'];opts=q.get('options',[])
 must(q.get('subject') in sub and len(q.get('stem',''))>=20,f'{qid}: disciplina/enunciado inválido')
 must(len(opts)==4 and len(set(str(x).strip().casefold() for x in opts))==4,f'{qid}: opções inválidas/duplicadas')
 must(type(q.get('answer')) is int and q['answer'] in range(4),f'{qid}: resposta inválida')
 must(len(q.get('explanation',''))>=38,f'{qid}: comentário curto/ausente')
 must('Autoral' in q.get('origin',''),f'{qid}: origem não declarada')
 if '[conceito]' in q.get('stem',''):
  must(q['stem'].count('[conceito]')==1,f'{qid}: descrição incompleta ou mascaramento excessivo')
 if q.get('kind')=='fixacao':
  answer=opts[q['answer']].casefold()
  plain=q.get('stem','').casefold().replace('[conceito]','')
  # Target term must not be spelled elsewhere in statement, except inside another unrelated word.
  if len(answer)>4 and re.search(r'(?<!\w)'+re.escape(answer)+r'(?!\w)',plain):issues.append(f'{qid}: a resposta aparece na própria pergunta')
for s in S:
 sids=s['qids'];m=Counter(byq[id]['subject'] for id in sids if id in byq)
 must(len(sids)==len(set(sids))==30,f'{s["id"]}: simulado não contém 30 questões distintas')
 must(all(m[k]==5 for k in sub),f'{s["id"]}: simulado sem 5 questões por disciplina')
 must(sum(weights.get(byq[x]['subject'],0) for x in sids)==100,f'{s["id"]}: pontuação divergente')
 must(s['duration']==10800,f'{s["id"]}: duração não é 3h')
for t in T:
 must(t.get('routeDay') in byd,f'{t["id"]}: sem data principal')
 must(t['id'] in byd[t['routeDay']].get('topicIds',[]),f'{t["id"]}: falta na data vinculada')
 must(t.get('verifiedLesson') is False,'Campo de cobertura foi marcado como verificado sem revisão independente')
for file in ['index.html','sw.js','src/styles.css','src/app.js','src/data/course.js','.github/workflows/pages.yml']:
 must((root/file).is_file(),f'Arquivo obrigatório ausente: {file}')
for item in c['sources']:
 if item['url'].startswith('public/') or item['url'].startswith('./public/'):
  must((root/item['url'].lstrip('./')).exists(),f'PDF de referência não encontrado: {item["url"]}')
report={'version':c.get('version'),'sessions':len(D),'theory_and_revision_days':len(D)-len(S),
 'sims':len(S),'scheduled_days':{k:daycounts[k] for k in daycounts},
 'questions_total':len(Q),'daily_question_appearances':sum(len(x['qids']) for x in D if x['subject']!='S'),
 'sim_question_appearances':sum(len(x['qids']) for x in S),
 'question_categories':dict(kinds),'flashcards':len(c['flashcards']),
 'verticalized_topics':len(T),'routed_topics':sum(bool(x.get('routeDay')) for x in T),
 'independently_editorially_verified_topics':sum(bool(x.get('verifiedLesson')) for x in T),
 'minimum_lesson_words':min(len(d['deepTheory'].split()) for d in D if d['subject']!='S'),
 'maximum_lesson_words':max(len(d['deepTheory'].split()) for d in D if d['subject']!='S'),
 'verified_real_IBGP_questions':0,
 'structure_passed':not issues,'issues':issues,'review_warnings':warnings}
(root/'AUDITORIA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Traceable CSV: one row per official subtopic, plus fixed study day and selected questions.
with (root/'MATRIZ_DE_COBERTURA.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.writer(f,delimiter=';');writer.writerow(['ID do tópico','Disciplina','Subtópico do edital verticalizado','Prioridade didática','Dia principal','Data','Tema da aula','Retomadas','ID(s) das questões associadas','Estado de validação'])
 for t in T:
  d=byd[t['routeDay']]
  writer.writerow([t['id'],c['subjects'][t['subject']],t.get('name'),t.get('priority',''),d['id'],d['date'],d['title'],', '.join(t.get('secondaryDays',[])),', '.join(t.get('questionIds',[])),'Roteirizado; não certificado individualmente'])
notes='\n'.join('- '+w for w in warnings) or '- Nenhum alerta de concentração.'
md=f'''# Auditoria — Miriam Estudos (reconstrução de 47 dias)\n\n## Integridade automática\n\n- **47 datas fixas**, de 20/10/2026 a 12/12/2026, sem domingos: {len(D)==47}.\n- **43 sessões de teoria/revisão**, cada uma com 8 questões fixas.\n- **4 simulados de 30 questões** com pontuação máxima de 100 e os seis pesos oficiais.\n- **{len(Q)} questões autorais** no banco ({kinds['caso']} casos aplicados, {kinds['fixacao']} fixações de conceito, {kinds['leitura']} leituras ativas, {kinds['original']} do banco anterior).\n- **{len(c['flashcards'])} flashcards** e **{len(T)} subtópicos organizados em datas**.\n- **{report['minimum_lesson_words']} a {report['maximum_lesson_words']} palavras** de teoria explicativa por sessão.\n- **Questões oficiais autenticadas da IBGP: 0.**\n- **Resultado estrutural: {'PASSOU' if not issues else 'FALHOU'}.**\n\n## Alertas de carga por dia\n\n{notes}\n\n## Problemas estruturais\n\n{chr(10).join('- '+x for x in issues) if issues else '- Nenhum identificado pelos testes implementados.'}\n\n## Limitações que NÃO podem ser ignoradas\n\nA criação de uma página para cada data, a presença de explicações e a vinculação dos 243 subtópicos **não equivalem à auditoria jurídica e pedagógica integral** do edital. Há tópicos amplos cujo aprofundamento pode exigir leitura adicional da legislação. Os itens de fixação de conceitos e leitura ativa são de nível fundamental, não possuem o mesmo grau de elaboração de uma prova real da IBGP.\n\nTodas as questões são autorais, com gabarito e explicação, mas **a auditoria de código não prova que todas as alternativas, respostas, remissões legais e comentários foram revisados independentemente**.\n\nAs três leis municipais anexadas pelo usuário podem não estar consolidadas para a data da prova. Conferir atualizações oficiais antes de decorar números, alíquotas, prazos ou procedimentos. Os simulados podem reutilizar o banco para treino, embora cada simulado tenha 30 identificadores distintos internamente.\n\nA atualização do GitHub depende do envio dos arquivos ao repositório; este ZIP não altera automaticamente o endereço já publicado.\n'''
(root/'AUDITORIA.md').write_text(md,encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(issues))
