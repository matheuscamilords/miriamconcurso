# Miriam Estudos — Agente Fiscal de Tributos (São João del-Rei/MG)

**Versão funcional de desenvolvimento, ainda NÃO certificada como curso preparatório completo.**

Plataforma estática gratuita, inteiramente local, para o cargo **325 — Agente Fiscal de Tributos**, Edital 02/2026, IBGP, prova prevista em 13/12/2026. As aulas e exercícios podem ser usados sem API, conta, mensalidade ou login. Os arquivos PDF anexados foram incluídos para consulta. O site contém alertas transparentes sobre pendências de completude e vigência jurídica.

## Como utilizar agora

1. Extraia o ZIP mantendo suas pastas.
2. Abra um terminal **dentro da pasta `miriam-estudos`**.
3. Se houver Python instalado, execute `python -m http.server 8000` (Windows) ou `python3 -m http.server 8000` (Linux/macOS).
4. Acesse **http://localhost:8000/** pelo navegador. Não abra `index.html` diretamente por `file://`, pois os módulos JavaScript podem sofrer bloqueio de segurança.
5. Clique em **Iniciar estudo de hoje** ou escolha uma data em **Cronograma**.

### O que está implementado

- 47 sessões datadas de 20/10 a 12/12, com domingos reservados ao descanso;
- 42 sínteses introdutórias originais, quatro simulados de 30 questões e uma revisão final, com indicações de duração (duração planejada, **não garantida** pela extensão atual das aulas);
- 144 questões autorais com quatro alternativas, explicações e assunto, reutilizáveis para treino e revisão espaçada; quatro simulados de 30 questões usam **120 questões distintas entre si**;
- sistema de respostas, cálculo de acertos e nota ponderada, cronômetro de 3 horas e correção do simulado após entrega;
- 144 flashcards, classificação de dificuldade, marcações e caderno de erros;
- edital verticalizado interativo com 243 subtópicos, marcações de primeira/segunda/terceira passagem e ligação preliminar às sessões;
- estatísticas provenientes apenas das respostas e registros da estudante;
- tema escuro, layout responsivo, persistência em `localStorage`, exportação e importação de backup JSON;
- cache offline dos principais arquivos após a primeira visita bem-sucedida em HTTPS e acesso aos PDFs municipais fornecidos.

## O que NÃO está concluído

**Esta versão não atende integralmente às exigências de profundidade e cobertura do prompt de origem.**

- Em 243 subtópicos do roteiro, apenas 50 apresentaram correspondência textual preliminar suficientemente clara com alguma aula. **Isso não significa que os 50 foram revisados e aprovados por especialista; 193 carecem de validação e possível produção didática específica.** A vinculação de rota para todos os 243 serve apenas para navegação e *não* constitui prova de cobertura.
- As sínteses introdutórias são curtas para preencher com autonomia sessões de duas horas e meia; precisa-se aprofundar o curso e produzir exercícios inéditos adicionais nos pontos ainda não abordados.
- A auditoria de enunciados é estrutural: **não ocorreu revisão jurídico-pedagógica humana independente, individualizada, de todas as questões**. Os comentários são fundamentações sintéticas, e nem todos analisam cada alternativa errada individualmente.
- **Zero questões reais da IBGP** foram reproduzidas ou autenticadas; todas as 144 estão corretamente marcadas como autorais.
- As versões dos textos municipais anexados **não foram certificadas como consolidadas até a data exigível pelo edital**. Há normas posteriores que exigem verificação específica, sobretudo no Código Tributário.
- O teste de navegador gráfico automatizado ficou bloqueado por restrição de navegação da infraestrutura de execução. Há testes estruturais e de execução do aplicativo em ambiente simulado; **isso não equivale a uma validação visual cross-browser**.
- O projeto não foi publicado no GitHub: a publicação depende do usuário ou da autorização de acesso ao repositório.

**Não empregar esta versão como único material de preparação até que as pendências sejam eliminadas.**

## Publicação gratuita no GitHub Pages

É possível publicar o estado atual, respeitando os avisos pedagógicos, em um repositório privado ou público conforme políticas de visibilidade do GitHub Pages (as condições de visibilidade e planos devem ser conferidas). Para facilitar a publicação gratuita, use um repositório **público**:

1. Entre no GitHub e crie um repositório público chamado `miriam-estudos`, **sem** criar README inicial. Não é necessário instalar React, Node ou dependências.
2. Descompacte o ZIP e abra terminal dentro da pasta `miriam-estudos`.
3. Execute os comandos a seguir, **trocando `SEU-USUARIO` pelo usuário real no GitHub**:

```bash
git init
git branch -M main
git add .
git commit -m "Adicionar plataforma Miriam Estudos"
git remote add origin https://github.com/SEU-USUARIO/miriam-estudos.git
git push -u origin main
```

4. No repositório do GitHub, abra **Settings → Pages → Build and deployment → Source** e escolha **GitHub Actions**.
5. Na aba **Actions**, aguarde o workflow `Publicar Miriam Estudos`. Caso ele ainda não esteja ativo, execute `Run workflow` manualmente.
6. O endereço esperado após a publicação será `https://SEU-USUARIO.github.io/miriam-estudos/`. **Confirme pelo próprio GitHub se a implantação ocorreu antes de divulgar.**

O workflow `.github/workflows/pages.yml` executa a auditoria estrutural e publica os arquivos estáticos. O JavaScript usa referências relativas, que funcionam em subdiretórios de repositórios do GitHub Pages.

## Estrutura e atualização

```text
index.html                     página inicial
src/styles.css                 interface adaptável
src/app.js                     navegação, simulados, progresso e backup
src/data/course.js             base integrada de conteúdos
scripts/sessions.tsv           planejamento e sínteses editáveis
scripts/questions.tsv          banco de questões autorais
scripts/generate.py            recompila src/data/course.js
scripts/audit.py               verificações de consistência
scripts/smoke.mjs              teste sem navegador físico
scripts/normative_readings.json   trechos literais dos PDFs fornecidos
public/fontes/                 documentos oficiais fornecidos
MATRIZ_DE_COBERTURA.csv        rastreabilidade com ressalvas de validação
AUDITORIA.md/json             resultado da auditoria automática
sw.js                         cache offline em HTTPS
.github/workflows/pages.yml   publicação no GitHub
```

Para atualizar uma aula ou uma questão:

1. Edite `scripts/sessions.tsv` ou `scripts/questions.tsv` (o caractere `|` separa campos: **não o insira livremente nos textos**).
2. Execute `python3 scripts/generate.py`. O script usa `scripts/verticalizado-extraido.txt` e a base de leituras legais anexas.
3. Execute `python3 scripts/audit.py` e `node scripts/smoke.mjs` (se Node estiver disponível).
4. Faça commit e push. **Preserve os IDs das sessões e questões já respondidas** para não perder o vínculo com backups antigos.
5. Se alterar recursos offline, incremente `CACHE` no arquivo `sw.js` (por exemplo, de `v1` para `v2`) e confirme a atualização após publicar.

### Backup e privacidade

O progresso fica no `localStorage` do navegador e não se sincroniza entre celulares e computadores. A limpeza dos dados do navegador pode apagá-lo. Use **Ajustes → Exportar backup JSON** periodicamente e **Ajustes → Importar backup** no novo dispositivo. A importação pede confirmação antes de substituir dados. O arquivo JSON contém respostas e progresso individual, que devem ser mantidos em local seguro.

## Fontes normativas e autorais

Edital nº 02/2026 retificado, retificação nº 01, Anexos I/III/IV, edital verticalizado e as três normas municipais entregues pelo solicitante. Há links para Planalto, ALMG, Câmara Municipal de São João del-Rei e site da IBGP na tela Biblioteca. A atenção a prazo de vigência e às alterações posteriores está destacada no curso.

As prioridades P1/P2/P3 são **sugestões do roteiro didático**, não classificação oficial da banca.

## Auditoria e qualidade

Execute `python3 scripts/audit.py` e leia `AUDITORIA.md`. A consistência estrutural verifica número e datas de sessões, formato e unicidade de questões, alternativas, pesos dos simulados, cartões e ligações de navegação. `node scripts/smoke.mjs` executa renderização simulada e testa abertura das 47 sessões, correção de questão, nota de simulado, flashcards, edição de dados locais e navegação básica, mas não valida CSS real em celular.

**Licença:** arquivos de autoria do projeto podem ser editados para uso próprio; os PDFs normativos conservam sua origem e eventuais restrições aplicáveis. Não há licença ou afiliação da banca IBGP.
