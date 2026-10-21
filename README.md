# Miriam Estudos — reconstrução de 47 datas (20/10–12/12/2026)

Curso estático para a candidata Miriam, cargo 325 — **Agente Fiscal de Tributos**, São João del-Rei/MG, concurso IBGP, Edital 02/2026 retificado. O conteúdo está no próprio site, e não depende de chamada à IA ou serviço pago durante as sessões.

## Conteúdo efetivamente incluído

- **47 datas fixas e navegáveis**, com estudo de segunda a sábado e descanso nos domingos.
- **43 sessões com teoria autoral individualizada**: 42 aulas disciplinares e uma revisão final; quatro datas são simulados completos.
- **8 questões fixas por aula** (344 posições de exercícios), todas com quatro alternativas, gabarito e comentários; contém explicações básicas, casos aplicados e leitura ativa.
- **371 questões autorais no banco**, sendo 144 do banco anterior, 89 situações aplicadas novas, 84 de fixação de conceitos e 54 de interpretação do texto; **zero questões reais da IBGP autenticadas**.
- **4 simulados com 30 questões** e 100 pontos, com cinco questões de cada matéria e os pesos oficiais.
- **371 flashcards**, caderno de erros, cronômetro, notas, estatísticas, marcações do edital, backup JSON e funcionamento responsivo.
- **243 subtópicos do edital verticalizado distribuídos em datas**, com matriz de rastreabilidade e alertas específicos de sobrecarga temática.
- PDF do edital, anexos, Lei Orgânica, Estatuto Municipal e Código Tributário Municipal anexados para consulta.

## Atenção: diferença entre implementação e certificação

**O site foi reconstruído para todas as datas, mas não posso declarar que a cobertura jurídico-pedagógica integral foi certificada.** Há aulas com 14–27 subtópicos indexados para uma única sessão, o que sinaliza risco de profundidade insuficiente. O guia textual possui aproximadamente 450–735 palavras por data, mais as questões, fontes e atividades: a duração de 2h30 inclui consulta das referências legais, exercícios, correção e revisão, não leitura contínua da síntese.

A auditoria automática verifica arquivo, cronologia, pontuação, gabaritos bem-formados, quantidades, roteirização e ausência de mistura de **disciplinas**. **Não comprova** que todos os 243 subtópicos foram ensinados com profundidade equivalente, nem que cada questão jurídica foi validada por revisor humano independente. Alguns exercícios são de memorização básica e não pretendem reproduzir o nível de dificuldade de uma prova real. As leis municipais em PDF podem estar desatualizadas; verifique a redação oficial consolidada e as regras temporais do edital.

Consulte [AUDITORIA.md](AUDITORIA.md), [MATRIZ_DE_COBERTURA.csv](MATRIZ_DE_COBERTURA.csv) e [CRONOGRAMA_FIXO.csv](CRONOGRAMA_FIXO.csv) antes de utilizar como fonte exclusiva.

## Atualizar o repositório que você já possui

Repositório identificado pelo usuário: **https://github.com/matheuscamilords/miriamconcurso**.

1. Baixe o ZIP e extraia. Abra a pasta `miriam-estudos`.
2. Em https://github.com/matheuscamilords/miriamconcurso, clique em **Add file → Upload files**.
3. Arraste **o conteúdo de dentro da pasta** para a raiz do repositório, inclusive `index.html`, `src/`, `public/`, `scripts/` e `.github/`. O GitHub pode ter limitações para envio de diretórios/pastas ocultas pelo navegador; se necessário, use o GitHub Desktop para atualização completa.
4. Confirme a substituição dos arquivos existentes no commit. Se a interface impedir substituir arquivos via upload, use **GitHub Desktop** para clonar o repositório, copiar o conteúdo e executar commit/push; não apague arquivos sem ter backup.
5. Vá a **Settings → Pages** e mantenha **GitHub Actions**. Acompanhe **Actions → Publicar Miriam Estudos**.
6. Após sucesso, acesse **https://matheuscamilords.github.io/miriamconcurso/**. Pode ser necessário atualizar a aba para receber os novos arquivos; o service worker desta edição usa prioridade à rede.

**Este pacote não altera seu GitHub automaticamente.** O progresso salvo no navegador é mantido sob a mesma chave; se houver progresso importante da versão antiga, exporte backup antes de atualizar.

## Desenvolvimento e auditoria

Não são necessários React, Node nem outras dependências em tempo de execução. Opcionalmente, sirva a pasta localmente com `python -m http.server 8000` e abra `http://localhost:8000`.

- `scripts/aulas_aprofundadas.py` — texto individual de cada data de aula;
- `scripts/casos_resolvidos.py` — oficinas didáticas por aula;
- `scripts/questoes_casos.txt` — exercícios aplicados próprios da data;
- `scripts/course-data-original.json` — matriz base de sessões, leis e questões anteriores;
- `scripts/rebuild_complete.py` — regeneração determinística dos dados (não reordena sessões);
- `scripts/audit.py` — integridade e geração de relatórios e matriz de cobertura;
- `scripts/smoke.mjs` — teste de execução do aplicativo simulado;
- `src/data/course.js` — todo o conteúdo já integrado para o site publicar;
- `.github/workflows/pages.yml` — auditoria e implantação automática pelo GitHub Pages.

Para regenerar, execute `python scripts/rebuild_complete.py`, `python scripts/audit.py` e `node scripts/smoke.mjs`. O teste visual de Chromium local foi bloqueado por política do ambiente, de modo que não se afirma validação em navegador real.

**Uso pedagógico independente**; não afiliado ao IBGP, à Prefeitura nem a cursos comerciais.
