# Dashboard de Inadimplência

Solução de automação desenvolvida para otimizar a rotina da Coordenação de Cobrança, eliminando o filtro manual de relatórios e entregando um painel interativo com foco em agilidade de ação.

---

## Primeiros Passos

1. **Insira o Relatório:** Coloque o arquivo `.csv` exportado do sistema (ex: `parcelas_cobranca_2026-09-25.csv`) dentro da pasta **`Arquivo Original`**.
2. **Execute o Orquestrador:** Dê um duplo clique no arquivo **`run.bat`**.
3. **Instalação Automática:** O script verificará se o Python está presente no sistema (caso não esteja, fará o download e instalação silenciosa), instalará a biblioteca `pandas` e exibirá a lista de relatórios disponíveis.
4. **Seleção:** Digite o número correspondente ao relatório que deseja analisar e aperte **Enter**.
5. **Resultado:** O sistema processará os dados com precisão matemática determinística, gerará o Dashboard Interativo em HTML na pasta **`Arquivo Final`** e abrirá o relatório automaticamente no seu navegador padrão.

---

## O que a Solução Faz
* **Limpeza de Dados:** Trata automaticamente inconsistências de datas mistas e converte valores monetários em texto para formatos numéricos flutuantes.
* **Filtro de Inadimplência:** Considera estritamente contratos com status **ATIVO**, parcelas em status **ABERTA** e com data de vencimento anterior à data de análise do relatório[cite: 4].
* **Interatividade (UX):** No Dashboard HTML gerado, a Renata pode:
  * Clicar diretamente no número do telemóvel para abrir uma conversa no **WhatsApp** com o cliente já com mensagem pré-formatada.
  * Clicar no botão **"Copiar Mensagem"** para copiar instantaneamente os dados formatados (empreendimento, nome, telemóvel, contrato e valor devido) para a área de transferência.

---

## Tecnologias Utilizadas
* **Python** (Processamento de dados e engenharia determinística).
* **Pandas** (Limpeza, tratamento e agregação financeira).
* **HTML5, CSS3 & JavaScript** (Geração de interface de dashboard leve e interativa, sem necessidade de servidores externos).
* **Batch Script (.bat)** (Automação de ambiente e orquestração).

---

## 📂 Estrutura de Pastas do Projeto
```text
├── Arquivo Original/       # Onde o usuário coloca o CSV bruto exportado
├── Arquivo Final/          # Onde o sistema salva o Dashboard HTML gerado
├── main.py                 # Script principal de processamento de dados e HTML
├── run.bat                 # Orquestrador automático para ambiente Windows
└── README.md               # Documentação da solução
