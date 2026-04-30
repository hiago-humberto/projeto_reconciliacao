# 🛡️ Audit Intelligence Hub | Motor de Reconciliação Financeira (Enterprise)

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Data_Lake](https://img.shields.io/badge/Arquitetura-Data_Lake_(Parquet)-000000?style=for-the-badge)

## 📌 O Problema de Negócio
Em auditorias contábeis e rotinas financeiras de grandes corporações, o cruzamento de dados entre o Sistema de Gestão (ERP, como TOTVS/SAP) e Extratos Bancários de **múltiplas instituições** (Itaú, Bradesco, Santander, etc.) é um caos operacional. Isso gera lentidão, alto risco de erro humano e dificuldade na identificação rápida de fraudes, pagamentos duplicados ou inadimplência.

## 💡 A Solução (De Script para Plataforma)
Este projeto evoluiu de um script procedimental para uma **Plataforma de Engenharia de Dados Financeiros**. Ele não apenas automatiza a reconciliação, mas possui uma **arquitetura desacoplada** com interface visual (Streamlit) e processamento robusto em *backend*. O motor extrai, limpa, cruza as bases e gera Dashboards Executivos em milissegundos, salvando o histórico em um Data Lake otimizado.

### ⚙️ Funcionalidades e Arquitetura de Dados
1. **Extração Multi-Fontes & Orquestração:** Leitura paralela de arquivos `.csv` simulando exportações do ERP e de múltiplos bancos simultaneamente, gerenciados por um orquestrador central.
2. **Data Quality (Fail-Fast):** O motor possui travas de segurança. Ele valida dinamicamente o *Schema* (colunas esperadas) e aplica validação de conteúdo (ex: bloqueia valores financeiros negativos), interrompendo a execução antes de gerar dados corrompidos.
3. **Higienização Performática:** Empilhamento inteligente de dados (`pd.concat`) e uso de *Regex* vetorizado (`str.replace`) para padronizar descrições bancárias sujas, abolindo loops lentos.
4. **Transformação e Cruzamento:** Utilização avançada do `pandas` para um `LEFT JOIN` (merge) `1:m`, calculando discrepâncias e mantendo a rastreabilidade da origem bancária.
5. **Persistência em Data Lake (Arquitetura Medalhão):** Abandono de exportações pesadas em CSV no backend. Os relatórios são salvos utilizando `pyarrow` em formato `.parquet` colunar, divididos em camadas `raw/` e `processed/`, garantindo versionamento com *timestamps* (Idempotência).

## 🛠️ Stack Tecnológica
* **Python 3.x:** Linguagem base para automação e lógica de negócios.
* **Pandas & NumPy:** Manipulação vetorial, *merge* de bases e aplicação de regras heurísticas de negócio em cascata.
* **Streamlit & Plotly:** Frontend analítico desacoplado, gerando gráficos de risco e KPIs financeiros em tempo real.
* **PyArrow:** Motor de I/O para persistência de dados no formato Parquet.
* **Logging (Nativo):** Implementação de trilhas de auditoria ("caixa preta") para rastreabilidade de execução em produção.

---


## 🚀 Como Executar o Projeto

### 1. Clone este repositório:

```bash
git clone https://github.com/hiago-humberto/projeto_reconciliacao.git
```

### 2. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
```

### 3. Instale as dependências:

```bash
pip install -r requirements.txt
```

### 4. Inicie o servidor:

```bash
streamlit run app_web.py
```

### 5. Execute o motor de reconciliação:
Para demonstrar a evolução da arquitetura de software, este repositório possui duas versões do motor. Escolha qual deseja executar:

**Opção A: Versão Básica (Lógica Procedural)**
Executa o código em bloco único, ideal para entender a lógica matemática passo a passo.
```bash
python reconciliador_v1.py
```

**Opção B: Versão Avançada (Clean Code / Funções) ⭐ Recomendado**
```bash
python reconciliador_v2_funcoes.py
```
### 6. Resultado:

O resultado será exibido no terminal e o arquivo `relatorio_excecoes_auditoria.csv` será gerado na raiz do projeto apenas com as divergências.

---

## 📦 Requisitos

* Python 3.x instalado
* Pip instalado

---

## 📁 Estrutura do Projeto 
```
projeto_reconciliacao/
│
├── gerador_dados.py # Gera dados simulando ERP e extratos bancários
│
├── reconciliador_v1_basico.py # Versão inicial (processamento em bloco único)
├── reconciliador_v2_funcoes.py # Versão refatorada (uso de funções / clean code)
│
├── extrato_itau.csv # Gerado automaticamente
├── extrato_bradesco.csv # Gerado automaticamente
├── sistema_financeiro.csv # Gerado automaticamente
│
├── relatorio_excecoes_auditoria.csv # Gerado após execução da auditoria
│
└── README.md
```

---


## 💡 Observações

Caso o comando python não funcione, tente:
```bash
python3 gerador_dados.py
```


Caso o pip não funcione:
```bash
python -m pip install pandas
```
📊 Sobre o Projeto
Projeto desenvolvido com foco na intersecção entre Ciências Contábeis, Administração e Engenharia de Dados, visando otimizar processos de Controladoria Multi-bancos.