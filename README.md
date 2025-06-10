# 🔥 Monitor de Queimadas no Brasil - Análise Interativa

## 📝 Descrição do Projeto

Este projeto é uma solução de automação inteligente para o monitoramento de focos de queimadas no Brasil. A aplicação web interativa, construída com Streamlit, automatiza todo o processo de **coleta, tratamento, análise e visualização** de dados abertos disponibilizados pelo INPE.

O dashboard permite que o usuário explore os dados da última semana de forma dinâmica, aplicando filtros por localidade e dia para obter insights detalhados sobre a situação das queimadas no país.

### Funcionalidades Principais

-   **Dashboard Interativo:** Uma interface web amigável para visualizar e filtrar os dados.
-   **Análise Dinâmica:** Filtre por **Estado** para ver análises específicas daquela localidade. O dashboard se adapta para mostrar os biomas e o ranking de municípios mais afetados.
-   **Análise de Risco:** Uma tabela identifica as localidades (estados ou municípios) em situação mais crítica, com base em um índice que considera o total de focos, dias sem chuva e a intensidade do fogo.
-   **Análise Temporal:** Explore a distribuição de focos por hora e por dia da semana.
-   **Pipeline Automatizado:** Com um clique, execute o pipeline que baixa os dados mais recentes, processa e atualiza todo o dashboard.

## 📁 Estrutura de Pastas

```
GS1-RPA/
│
├── data/           # (Ignorado pelo Git) Dados brutos e processados
├── reports/        # (Ignorado pelo Git) Gráficos e tabelas gerados
├── src/            # Módulos da aplicação (coleta, processamento, análise)
│
├── .gitignore      # Arquivo para ignorar pastas e arquivos
├── app.py          # Script da aplicação Streamlit (interface)
├── main.py         # Script para execução do pipeline via terminal
├── requirements.txt
└── README.md
```

## 🚀 Como Executar

### Pré-requisitos

-   Python 3.8 ou superior
-   `pip` e `venv`
-   Git

### 1. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd GS1-RPA
```

### 2. Criar e Ativar o Ambiente Virtual

**No Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**No macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as Dependências

```bash
pip install -r requirements.txt
```

### 4. Executar a Aplicação Web

A principal forma de interagir com o projeto é através da interface Streamlit.

```bash
streamlit run app.py
```

Isso abrirá uma aba no seu navegador. Clique no botão **"Atualizar e Analisar Novos Dados"** para carregar os dados pela primeira vez e explorar o dashboard.

### 5. (Alternativo) Executar via Terminal

Você também pode executar o pipeline completo de forma silenciosa (sem a interface) pelo terminal.

```bash
python main.py
``` 