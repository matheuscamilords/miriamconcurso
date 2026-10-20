"""Attach short, faithful source-text snippets of user's municipal-law PDFs to relevant sessions."""
import json,fitz,re,pathlib
base=pathlib.Path(__file__).resolve().parents[1]
mapdoc={
 'c':('public/fontes/codigo-tributario-municipal-lei-4012-2006.pdf','Lei 4.012/2006 — Código Tributário Municipal'),
 'e':('public/fontes/estatuto-servidores-lei-5038-2014.pdf','Lei 5.038/2014 — Estatuto dos Servidores'),
 'o':('public/fontes/lei-organica-sao-joao-del-rei.pdf','Lei Orgânica municipal')
}
# 1-based pages, mapped to the relevant source-specific module. PDF is a historical snapshot; check alterations.
lookup={
 'Fundamentos da tributação':('c',[1,2]),
 'Estatuto municipal: ingresso':('e',[4,5,6]),
 'Lei Orgânica: autonomia':('o',[2,3]),
 'CTN: competência':('c',[1,2]),
 'Estatuto: estágio probatório':('e',[10,11,12]),
 'Tributos municipais: IPTU':('c',[8,9]),
 'ISSQN e prestação':('c',[19,20]),
 'Lei Orgânica: Câmara':('o',[16,17]),
 'ITBI: transmissão':('c',[29,30]),
 'Código Tributário Municipal: administração':('c',[1,2,3]),
 'Estatuto municipal: vantagens':('e',[22,23]),
 'Estatuto: vantagens':('e',[22,23,39]),
 'Responsabilidade tributária':('c',[3,4])
}
allDocs={key:fitz.open(base/path) for key,(path,_) in mapdoc.items()}
rows=[line.split('|') for line in (base/'scripts/sessions.tsv').read_text().splitlines() if line.strip()]
readings={}
for i,row in enumerate(rows):
 title=row[1]
 entry=next((v for k,v in lookup.items() if title.startswith(k)),None)
 if not entry:continue
 key,pages=entry
 snippets=[]
 for page in pages:
  body=allDocs[key][page-1].get_text(sort=True)
  body=re.sub(r'(?m)^\s*(?:Prefeitura Municipal de São João Del Rei|Prefeitura Municipal de São João del-Rei|\d{1,3}|Página \d+ de \d+)\s*$','',body)
  body=re.sub(r'\n\s*\n+', '\n\n', body)
  snippets.append({'page':page,'text':body[:2600]})
 readings[f'D{i+1:02d}']={'title':mapdoc[key][1], 'url':'./'+mapdoc[key][0], 'sections':snippets,'warning':'Leitura literal do PDF recebido; confira legislação consolidada e eventuais alterações aplicáveis.'}
(base/'scripts/normative_readings.json').write_text(json.dumps(readings,ensure_ascii=False,indent=2))
print('Normative contextual readers:',len(readings),'days:',', '.join(readings))
