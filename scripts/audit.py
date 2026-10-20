#!/usr/bin/env python3
import pathlib,json,datetime,collections,sys,re
base=pathlib.Path(__file__).resolve().parents[1];o=json.loads((base/'scripts/course-data.json').read_text());issues=[]
def check(condition,msg):
 if not condition:issues.append(msg)
days=o['days'];qs=o['questions'];qmap={q['id']:q for q in qs};sid={s['id']:s for s in o['sims']};subjects=o['subjects'];weights=o['weights'];topics=o['topics']
check(len(days)==47,'Existem '+str(len(days))+' sessões; deveriam ser 47')
check(len(set(d['date'] for d in days))==len(days),'Datas duplicadas')
check(days[0]['date']=='2026-10-20' and days[-1]['date']=='2026-12-12','Datas limites divergentes')
for d in days:
 dt=datetime.date.fromisoformat(d['date'])
 check(dt.weekday()!=6,'Domingo obrigatório: '+d['date'])
 check(d['duration'] in (120,150,180),'Duração inválida: '+d['id'])
 check(len(d['theory'])>100,'Texto teórico insuficiente: '+d['id'])
 check(d['example'] and d['trap'] and d['source'],'Faltam exemplos/fonte: '+d['id'])
 if d['subject']!='S':check(4<=len(d['qids'])<=15,'Quantidade de questões inadequada: '+d['id'])
 check(all(qid in qmap for qid in d['qids']),'Questão ausente em '+d['id'])
check(len(o['sims'])==4,'Deveriam existir quatro simulados')
check(len(set(q['id'] for q in qs))==len(qs),'IDs de questões duplicados')
check(len(set(q['stem'].strip().casefold() for q in qs))==len(qs),'Enunciados duplicados')
for q in qs:
 check(len(q['stem'])>8 and len(q['options'])==4,'Questão incompleta '+q['id'])
 check(len(set(x.strip().casefold() for x in q['options']))==4,'Alternativas idênticas: '+q['id'])
 check(all(len(x.strip())>0 for x in q['options']),'Alternativa vazia: '+q['id'])
 check(type(q['answer']) is int and 0<=q['answer']<4,'Gabarito malformado: '+q['id'])
 check(len(q['explanation'])>=20,'Comentário insuficiente: '+q['id'])
 check(q['subject'] in subjects and bool(q['topic']) and 'Autoral' in q['origin'],'Falta disciplina/tópico/autoria: '+q['id'])
for s in o['sims']:
 check(len(s['qids'])==30,'Simulado com número errado: '+s['id'])
 check(len(set(s['qids']))==30,'Repetição dentro do simulado: '+s['id'])
 dist=collections.Counter(qmap[qid]['subject'] for qid in s['qids']);check(all(dist[k]==5 for k in subjects),'Distribuição irregular: '+s['id'])
 check(sum(weights[qmap[qid]['subject']] for qid in s['qids'])==100,'Pesos incorretos em '+s['id'])
 allDay=next((d for d in days if d['id']==s['dayId']),None);check(allDay is not None and allDay.get('simId')==s['id'],'Dia incompatível simulado: '+s['id'])
check(len(set(t['id'] for t in topics))==len(topics),'IDs de tópicos duplicados')
check(all(t.get('routeDay') in {d['id'] for d in days} for t in topics),'Tópicos sem rota')
check(len(o['flashcards'])==len(qs),'Flashcards incompletos')
check(all((base/p).is_file() for p in ['index.html','sw.js','src/app.js','src/styles.css','.github/workflows/pages.yml']),'Arquivo funcional/deploy ausente')
# Full content assertion deliberately separate; formal linkage is not validation.
verified=[t for t in topics if t.get('verifiedLesson')]
pedagogical_full=(len(verified)==len(topics) and all(len(d['theory'].split())>=350 for d in days if d['subject'] not in ['S','F']))
report={'days':len(days),'theory_sessions':len([d for d in days if d['subject'] not in ('S','F')]),'final_review_sessions':len([d for d in days if d['subject']=='F']),'simulations':len(o['sims']),'questions_unique':len(qs),'questions_autoral':len([q for q in qs if q['origin'].startswith('Autoral')]),'questions_ibgp_verified':0,'daily_question_appearances':sum(len(d['qids']) for d in days),'mock_question_appearances':sum(len(s['qids']) for s in o['sims']),'flashcards':len(o['flashcards']),'verticalized_subtopics':len(topics),'linked_routes':len([t for t in topics if t['routeDay']]),'preliminary_text_matching_topics':len(verified),'not_pedagogically_validated':len(topics)-len(verified),'all_lessons_complete_and_verified':pedagogical_full,'structural_issues':issues}
(base/'AUDITORIA.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));(base/'AUDITORIA.md').write_text('# Auditoria de integridade — Miriam Estudos\n\n'+ '\n'.join(f'- **{k}**: {v}' for k,v in report.items() if k!='structural_issues')+'\n\n## Problemas estruturais encontrados\n'+('\n'.join('- '+x for x in issues) if issues else 'Nenhum, nas verificações automáticas implementadas.')+'\n\n## Ressalvas técnicas e pedagógicas\n\n- A correspondência textual dos tópicos **não comprova** cobertura integral do conteúdo; a vinculação de todos os 243 subtópicos às aulas é apenas roteiro de navegação.\n- Cada questão tem uma explicação, porém a auditoria automática não comprova a inexistência de erros de conteúdo jurídico, histórico, textual ou lógico.\n- As questões das sessões diárias são selecionadas de um banco estático e podem reaparecer em revisões; os quatro simulados usam 120 questões distintas entre si.\n- Esta edição contém somente questões autorais; não há questões reais da banca autenticadas.\n- Os PDFs das leis municipais foram disponibilizados pelo usuário e **não foram certificados como consolidações atualizadas**.\n- A plataforma não se declara integralmente alimentada ou certificada enquanto não atingir os requisitos de profundidade e revisão do prompt de origem.\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(1 if issues else 0)
