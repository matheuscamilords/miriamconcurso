from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
p=root/'src/app.js';s=p.read_text()
old="<h3>Explicação</h3>${d.deepTheory?deepTheoryHTML(d.deepTheory)"
new="<h3>Roteiro fechado desta data</h3><p><strong>Tempo recomendado:</strong> ${d.timePlan?.teoria||85} min teoria e leitura da fonte; ${d.timePlan?.questoes||45} min exercícios; ${d.timePlan?.revisao||20} min correção e revisão. As questões abaixo são as mesmas sempre que esta data for aberta.</p><div class=\"note\"><strong>Referências oficiais vinculadas ao dia (roteiro, não certificação de cobertura):</strong><ul>${(d.topicIds||[]).map(id=>{let t=course.topics.find(t=>t.id===id);return t?`<li>${esc(t.name)}</li>`:''}).join('')}</ul></div><h3>Explicação</h3>${d.deepTheory?deepTheoryHTML(d.deepTheory)"
assert old in s;s=s.replace(old,new)
start=s.index('function sourcePage(){');end=s.index('function settingsPage(){',start)
replacement='''function sourcePage(){let verified=course.topics.filter(t=>t.verifiedLesson).length;let itemCounts={};for(const q of course.questions){let k=q.kind||'original';itemCounts[k]=(itemCounts[k]||0)+1}return `${sectionHead('BIBLIOTECA E TRANSPARÊNCIA','Fontes, conteúdo e limites','Material organizado por datas, fontes de consulta e distinção entre integridade técnica e revisão intelectual.')}
<div class="warning"><strong>Material pedagógico reconstruído:</strong> 43 sessões com teoria particularizada, quatro simulados e ${course.questions.length} questões autorais no banco. Todas as 43 datas de aula possuem 8 questões previamente vinculadas. Há ${course.topics.length} subtópicos vinculados a datas; <strong>essa rota não comprova que cada subtópico foi suficientemente aprofundado ou juridicamente validado</strong>. ${course.topics.length-verified} subtópicos ainda carecem de certificação pedagógica individual. Nenhuma questão foi identificada como questão real autenticada da IBGP.</div>
<div class="panel"><h2>Como ler o material</h2><p>A teoria traz conceitos, explicações específicas da sessão, exemplos resolvidos e pontos de memorização. Os exercícios do dia são fixos, sem sorteio entre matérias. Alguns exercícios treinam conceitos essenciais ou compreensão da própria aula; não devem ser confundidos com provas passadas da banca.</p><p><strong>Origem do banco:</strong> ${itemCounts.caso||0} questões aplicadas criadas para as datas, ${itemCounts.fixacao||0} questões de conceitos da teoria, ${itemCounts.leitura||0} itens de recuperação do texto e ${itemCounts.original||0} questões do banco autoral anterior.</p><p>O site não transmite respostas para a nuvem: o progresso é guardado no navegador, e a opção de backup permite transferência manual.</p></div>
<div class="panel"><h2>Documentos e referências</h2>${course.sources.map(s=>`<div class="fileitem"><div><strong>${esc(s.name)}</strong><small>${esc(s.kind)}</small></div><a class="button ghost small" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">Abrir ↗</a></div>`).join('')}</div>
<div class="panel"><h2>Vigência das normas e cautelas</h2><p>O item 1.5 do edital e a introdução do Anexo IV utilizam regras temporais que exigem conferência de sua aplicação. O Código Tributário Municipal (2006), o Estatuto e a Lei Orgânica anexados podem não conter todas as alterações posteriores. Alíquotas, prazos, redações e fatos atuais devem ser conferidos em versões oficiais consolidadas.</p><p>Uma auditoria automática verifica quantidade, datas, formato e vínculos, mas não substitui a revisão jurídico-pedagógica independente do conteúdo de cada questão e das aulas.</p></div>`}
'''
s=s[:start]+replacement+s[end:]
p.write_text(s)
# Remove the obsolete cache-first behavior, which serves the old version indefinitely.
service=root/'sw.js';t=service.read_text();t=t.replace("const CACHE='miriam-estudos-v1'","const CACHE='miriam-estudos-v2026-10-reconstrucao-47'")
f=t.index("self.addEventListener('fetch'")
t=t[:f]+'''// Network-first for versioned lesson/code assets: publication updates are visible.
// For offline use fall back to previously cached material after the first visit.
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;
 const url=new URL(e.request.url);if(url.origin!==self.location.origin)return;
 e.respondWith(fetch(e.request).then(resp=>{if(resp.ok){const clone=resp.clone();caches.open(CACHE).then(c=>c.put(e.request,clone))}return resp}).catch(()=>caches.match(e.request)));});
'''
service.write_text(t)
