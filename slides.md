# Roteiro de Apresentação: Criação de Agentes de IA com Deep Agents
**Tema:** Da teoria à prática: construindo agentes inteligentes com ferramentas, memória e autonomia controlada.  
**Duração:** 45 minutos | **Linguagem:** Python | **Stack:** Deep Agents (LangChain), Google Gemini, ArXiv, FastAPI, uv  
**Público:** Desenvolvedores, engenheiros de software, especialistas técnicos e entusiastas de IA.

---

## Slide 1 — Abertura (2 min)

### No slide:
- Criação de Agentes de IA com Deep Agents (LangChain)
- Arquitetura: LLM, Tools, Skills, Memória e Subagentes
- Segurança e Human-in-the-Loop na prática
- Exemplo Real: Research Assistant com Google Gemini e arXiv

### Sua fala:
> "Olá a todos! Sejam muito bem-vindos. Hoje vamos entender na prática como construir agentes de inteligência artificial de verdade utilizando o framework **Deep Agents**, da LangChain.
> 
> A nossa proposta hoje é dar um passo além do paradigma de 'apenas conversar com um modelo de linguagem'. Vamos entender como estruturar sistemas autônomos capazes de receber um objetivo complexo, planejar etapas, consultar fontes científicas reais via ferramentas, aplicar procedimentos especializados através de Skills e trabalhar com autonomia governada e segura.
> 
> Ao longo da sessão, vamos percorrer a anatomia desses componentes e ver uma demonstração real implementada em Python com Google Gemini e arXiv. Vamos em frente!"

---

## Slide 2 — LLM Tradicional vs. Agente de IA (3 min)

### No slide:
| LLM Tradicional | Agente de IA |
| :--- | :--- |
| Recebe perguntas e gera respostas | Recebe objetivos e planeja a execução |
| Conhecimento estático (data de corte) | Consulta dados em tempo real via Tools |
| Não executa ações no mundo externo | Aciona APIs, lê/grava arquivos e delega tarefas |
| Sessões isoladas sem continuidade | Memória persistente e estado evolutivo |

### Sua fala:
> "Para começarmos alinhados: qual é a diferença fundamental entre um LLM comum e um Agente de IA?
> 
> Um LLM tradicional funciona como um mecanismo probabilístico de completude: você envia um texto e ele retorna uma resposta com base exclusivamente no conhecimento congelado no seu pré-treinamento. Ele não 'sabe' o que aconteceu ontem, não interage com sistemas e não toma iniciativas.
> 
> Já um Agente de IA utiliza o modelo de linguagem como um **motor de raciocínio**. O agente recebe um objetivo de alto nível, decide quais ferramentas precisa acionar, interpreta o retorno dessas ferramentas e itera em um ciclo de ação e reflexão até cumprir o objetivo. Se faltar informação, ele busca; se precisar salvar um arquivo, ele salva; se a tarefa for complexa, ele divide em etapas."

---

## Slide 3 — Anatomia de um Agente Moderno (3 min)

### No slide:
- **LLM (Raciocínio):** O cérebro que decide o próximo passo.
- **System Prompt:** Definição de papel, regras, restrições e tom.
- **Tools (Ação):** Funções executáveis (APIs, bancos, web, arXiv).
- **Skills (Procedimento):** Conhecimento especializado sob demanda (Agent Skills Spec).
- **Memory (Continuidade):** Informações que persistem entre sessões (`AGENTS.md`).
- **Subagents (Especialização):** Context Quarantine para tarefas específicas.
- **Human-in-the-Loop (Segurança):** Pausa para aprovação humana em ações críticas.

### Sua fala:
> "Esta é a anatomia completa de um agente em produção. Observem que o modelo de linguagem é apenas um dos componentes.
> 
> Para que o sistema opere com confiabilidade, precisamos cercá-lo de infraestrutura:
> - O **System Prompt** estabelece os limites operacionais e a postura.
> - As **Tools** conectam o agente ao ecossistema externo — no nosso caso, consultar o arXiv.
> - As **Skills** ensinam ao agente procedimentos passo a passo sem inchar o contexto inicial.
> - A **Memória** garante que preferências do usuário sobrevivam entre conversas.
> - Os **Subagentes** isolam contextos complexos para evitar alucinações.
> - E o **Human-in-the-Loop** garante que operações destrutivas ou de escrita passem pelo crivo humano."

---

## Slide 4 — O que é o Deep Agents? (3 min)

### No slide:
- Framework moderno da LangChain para agentes de tarefas complexas
- Decomposição automática e planejamento de tarefas
- Filesystem virtual integrado (`FilesystemBackend`) com isolamento seguro
- Suporte nativo à especificação aberta de **Agent Skills**
- Delegação nativa para subagentes síncronos e assíncronos
- Interrupções declarativas de Human-in-the-Loop (`interrupt_on`)

### Sua fala:
> "E onde entra o **Deep Agents**? Em vez de programarmos loops manuais de LangChain ou grafos complexos no LangGraph do zero para controlar chamadas de ferramentas e arquivos, o Deep Agents nos fornece um *harness* robusto e padronizado.
> 
> Ele já traz de fábrica: sistema de arquivos virtualizado com permissões seguras, descoberta progressiva de Skills conforme o padrão da indústria, middleware de Human-in-the-Loop que pausa e retoma o grafo exatamente de onde parou, e gerenciamento de memória em arquivos markdown.
> 
> Isso reduz dezenas de linhas de infraestrutura repetitiva e nos permite focar no domínio da nossa aplicação."

---

## Slide 5 — Arquitetura da Nossa Aplicação (3 min)

### No slide:
*(Exibir imagem da arquitetura `image.png` ou diagrama de blocos)*
- **Usuário:** Solicitação de pesquisa científica
- **Supervisor (Research Assistant):** Orquestrador com Deep Agents e Gemini 2.5 Flash
- **Tool:** Busca de preprints e metadados no repositório arXiv
- **Skill:** Análise metódica em `skills/scientific-article-analysis/SKILL.md`
- **Subagente:** Auditoria metodológica independente (`methodology-reviewer`)
- **Memória & Workspace:** Arquivo `AGENTS.md` e relatórios em `agent_workspace/reports/`

### Sua fala:
> "Esta é a arquitetura exata da aplicação que implementamos e que vamos rodar hoje.
> 
> Construímos um **Research Assistant**. O fluxo funciona assim:
> 1. O usuário pede um estudo sobre um tema científico.
> 2. O agente principal aciona a ferramenta do arXiv para obter artigos reais e seus resumos.
> 3. Ele carrega a Skill de análise científica para guiar o roteiro de avaliação (objetivo, desenho experimental, resultados e ameaças à validade).
> 4. Ele delega a checagem estatística e metodológica para um subagente especialista em auditoria acadêmica.
> 5. Respeita as preferências de escrita salvas na sua memória persistente.
> 6. Solicita autorização humana antes de gravar o relatório final no disco."

---

## Slide 6 — System Prompt: Diretrizes e Postura (3 min)

### No slide:
- Define o papel de liderança do Supervisor
- Estabelece regras obrigatórias de execução
- Orienta quando ativar skills e quando delegar a subagentes
- Restrições explícitas contra alucinações e especulações
- Implementado em: `app/agents.py` (`RESEARCH_SUPERVISOR_PROMPT`)

### Sua fala:
> "No código, em `app/agents.py`, temos o `RESEARCH_SUPERVISOR_PROMPT`.
> 
> Um bom System Prompt de agente não é um parágrafo genérico de 'seja prestativo'. Ele deve funcionar como um manual de operações com regras claras:
> 1. Instruímos o agente a sempre buscar fatos primeiro com `search_arxiv_articles`.
> 2. Definimos que ele deve seguir a skill `scientific-article-analysis`.
> 3. Determinamos quando acionar o subagente de metodologia.
> 4. E definimos o formato rígido de saída para os relatórios na pasta do workspace.
> 
> A clareza do System Prompt é o que garante que o LLM não tente inventar artigos nem resolva tudo em texto corrido superficial."

---

## Slide 7 — Tools: Conectando com o Mundo Externo (4 min)

### No slide:
- `@tool search_arxiv_articles`: Consulta à API oficial do arXiv
- Sem necessidade de chaves pagas: repositório científico público e aberto
- Retorna metadados estruturados: título, autores, data, categoria, resumo e link do PDF
- Implementado em: `app/tools.py`

### Sua fala:
> "Vejamos as Tools. Em `app/tools.py`, criamos a ferramenta `search_arxiv_articles` utilizando a biblioteca oficial do arXiv.
> 
> Por que o arXiv? Porque é aberto, gratuito e contém a vanguarda das publicações de computação, IA, física e matemática.
> 
> Uma ferramenta de agente deve ser cirúrgica: ela sanitiza os termos de busca, limita os resultados para não estourar o limite de tokens da janela de contexto e devolve um JSON estruturado com o que realmente importa: título, autores, ano, categoria e resumo. O modelo lê essa resposta e toma as próximas decisões com base em dados de fontes verificadas."

---

## Slide 8 — Skills: Conhecimento Procedural Sob Demanda (4 min)

### No slide:
- Baseado na especificação aberta **Agent Skills**
- Metadados no cabeçalho YAML (`name` e `description`)
- **Progressive Disclosure:** O agente só lê o corpo da skill quando a tarefa exige
- Etapas: Extração de Metadados -> Formulação do Problema -> Desenho Metodológico -> Resultados -> Limitações -> Relatório
- Implementado em: `skills/scientific-article-analysis/SKILL.md`

### Sua fala:
> "Muitos desenvolvedores cometem o erro de colocar todo o conhecimento da empresa ou todo o procedimento de análise dentro do System Prompt principal. Isso causa o problema de **Context Bloat** (inchaço de contexto): o modelo gasta tokens à toa e perde o foco.
> 
> No Deep Agents, utilizamos **Skills**. Na inicialização, o agente carrega apenas o nome e a descrição do cabeçalho YAML da skill. Quando o usuário pede uma análise crítica, o agente identifica a necessidade e lê o arquivo `SKILL.md` sob demanda.
> 
> Nossa skill estabelece um padrão rigoroso: ela proíbe aceitar conclusões sem analisar tamanho da amostra, variáveis de controle e limitações declaradas pelos autores."

---

## Slide 9 — Memória Persistente e Subagentes (4 min)

### No slide:
- **Memória (`agent_workspace/memories/AGENTS.md`):**
  - Continuidade entre threads e conversas
  - Diretrizes de idioma (Português/BR), tom acadêmico e regras de nomenclatura de relatórios
- **Subagentes (`methodology-reviewer`):**
  - Isolamento de contexto (*Context Quarantine*)
  - Foco exclusivo em auditoria estatística e viés experimental
  - O supervisor recebe apenas o parecer técnico consolidado

### Sua fala:
> "No Slide 9 abordamos dois pilares de escala: Memória e Subagentes.
> 
> A **Memória Persistente** fica salva no nosso arquivo `AGENTS.md`. Nela gravamos preferências que persistem entre execuções: idioma preferencial, rigor na formatação de citações e onde os arquivos devem ser salvos.
> 
> Já o **Subagente** resolve o desafio da especialização. Criamos o `methodology-reviewer`. Enquanto o agente principal cuida do diálogo e da síntese, o subagente recebe os dados do estudo em um contexto isolado — o que chamamos de *Context Quarantine*. Ele faz o papel do 'Revisor 2' de uma revista acadêmica: aponta fraquezas amostrais e inconsistências estatísticas e devolve apenas a conclusão para o agente principal."

---

## Slide 10 — Segurança e Human-in-the-Loop (4 min)

### No slide:
- Autonomia governada: permissões granulares no filesystem
- `FilesystemBackend(virtual_mode=True)`: bloqueia navegação fora do workspace
- `interrupt_on={"write_file": True}`: intercepta operações de escrita
- O agente congela no checkpoint do LangGraph aguardando autorização humana (`[S/n]`)

### Sua fala:
> "Autonomia não pode ser sinônimo de risco. Um agente autônomo em produção jamais deve ter passe livre para sobrescrever dados ou disparar ações externas sem supervisão quando o impacto for alto.
> 
> O Deep Agents resolve isso de duas formas elegantes:
> 1. O **Filesystem virtualizado** (`virtual_mode=True`) impede que o agente use caminhos relativos como `../` para acessar arquivos confidenciais do sistema operacional.
> 2. O **Human-in-the-Loop** através de `interrupt_on={"write_file": True}` pausa o grafo automaticamente. O agente elabora o relatório, mas para antes de gravar na pasta `reports/` e pergunta: *'Posso gravar este arquivo?'*. Se aprovarmos, ele grava; se rejeitarmos, ele descarta."

---

## Slide 11 — Demonstração Prática ao Vivo (8 min)

### No slide:
**Executando com `uv`:**
1. Verificação da estrutura e compilação:
   `uv run python main.py --check-only`
2. Pesquisa Científica com Human-in-the-Loop:
   `uv run python main.py -q "Mecanismos de Atenção em Transformers" --hitl`
3. Observação das chamadas de ferramentas e subagente nos logs
4. Aprovação da escrita e inspeção do relatório em `agent_workspace/reports/`
5. Demonstração da API com FastAPI e Swagger em `http://localhost:8000/docs`

### Sua fala:
> "Agora vamos ver tudo isso funcionando junto no terminal.
> 
> *(Executar no terminal: `uv run python main.py --check-only`)*
> Vejam que o `uv` carrega nosso ambiente em milissegundos e o Deep Agent compila todas as tools, subagentes e skills.
> 
> *(Executar: `uv run python main.py -q "Mecanismos de Atenção em Transformers" --hitl`)*
> Reparem no log estruturado com o Rich:
> - O agente acionou `search_arxiv_articles` e consultou os servidores do arXiv.
> - Em seguida, ativou a skill `scientific-article-analysis` com `read_file`.
> - Delegou a auditoria de validação ao subagente `methodology-reviewer` via ferramenta `task`.
> - E agora vejam na tela: ele congelou na interrupção de Human-in-the-Loop!
> 
> Ele me pergunta se autorizo a escrita de `relatorio_transformers_attention.md`. Vou digitar 's'.
> Pronto! Operação aprovada, resposta concluída. E se abrirmos a pasta `agent_workspace/reports/`, temos aqui um relatório de 10 páginas em Markdown, com citações, metodologia, limitações e referências."

---

## Slide 12 — Encerramento e Conclusão (4 min)

### No slide:
- Agentes são **sistemas de software**, não apenas prompts
- **Tools** garantem dados reais e verificáveis
- **Skills** conferem metodologia e reduzem inchaço de contexto
- **Memória** assegura coerência a longo prazo
- **Subagentes** dividem a complexidade
- **HITL & Sandbox** garantem governança corporativa

### Sua fala:
> "Para encerrar, o principal aprendizado que quero deixar para vocês hoje é:
> 
> **Construir agentes inteligentes vai muito além da engenharia de prompt.**
> 
> Um prompt bem escrito é apenas o ponto de partida. O que transforma um modelo de linguagem em um agente confiável de nível de produção é a **arquitetura de software** ao redor dele: ferramentas bem delimitadas, procedimentos desacoplados via Skills, memória persistente, divisão de trabalho com subagentes e, acima de tudo, mecanismos de segurança e supervisão humana.
> 
> O código completo está estruturado, modular e pronto para ser explorado. Muito obrigado pelo tempo de vocês e vamos abrir agora para perguntas!"
