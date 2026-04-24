# 🔍 Motor de Reconciliação Financeira e Auditoria Automatizada (Multi-Bank)

## 📌 O Problema de Negócio
Em auditorias contábeis e rotinas financeiras de grandes corporações, o cruzamento de dados entre o Sistema de Gestão (ERP) e Extratos Bancários de **múltiplas instituições** (Itaú, Bradesco, Santander, etc.) é um caos operacional. Isso gera lentidão, alto risco de erro humano e dificuldade na identificação rápida de fraudes, pagamentos duplicados ou inadimplência.

## 💡 A Solução (V2.0)
Este projeto é um script avançado de **Engenharia de Dados Financeiros** construído em Python. Ele não apenas automatiza a reconciliação, mas também **consolida (empilha)** automaticamente extratos de diferentes bancos antes de cruzar com o ERP (TOTVS/SAP). O motor extrai, limpa, padroniza, cruza as bases e gera um relatório classificado por "Status Contábil" em milissegundos.

### ⚙️ Funcionalidades Principais (Pipeline de Dados)
1. **Extração Multi-Fontes:** Leitura de arquivos `.csv` simulando exportações do ERP e de dois bancos diferentes simultaneamente.
2. **Data Cleansing e Concatenação:** Empilhamento inteligente de dados (`pd.concat`) e padronização de chaves de ligação a partir de descrições bancárias sujas.
3. **Transformação e Cruzamento:** Utilização da biblioteca `pandas` para realizar um `LEFT JOIN` (merge) `1:m`, garantindo que nenhuma duplicidade bancária passe despercebida.
4. **Regras de Negócio e Rastreabilidade:** - Tratamento de valores nulos e cálculo automático de discrepâncias.
   - Manutenção da origem bancária (rastreabilidade de onde o dinheiro caiu).
   - Uso de `NumPy` para classificação inteligente de **Status** ("Conciliado", "Pendente" ou "Duplicado").
5. **Carga (Relatório de Exceções):** Filtro inteligente que ignora transações "OK" e exporta apenas as inconsistências para análise da auditoria.

## 🛠️ Tecnologias Utilizadas
* **Python 3.x:** Linguagem base para automação.
* **Pandas:** Manipulação, concatenação (`concat`) e cruzamento (`merge`) de dados tabulares.
* **NumPy:** Vetorização de regras de negócio em cascata para performance e classificação de status.


## 🚀 Como Executar o Projeto

### 1. Clone este repositório:

```bash
git clone https://github.com/hiago-humberto/projeto_reconciliacao.git
```

### 2. Acesse a pasta do projeto:

```bash
cd projeto_reconciliacao
```

### 3. Instale a biblioteca necessária:

```bash
pip install pandas
```

### 4. Execute o gerador de dados (simula a exportação do ERP e dos Bancos):

```bash
python gerador_dados.py
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


```
---

## 💡 Observações
```
```bash
Caso o comando python não funcione, tente:

python3 gerador_dados.py

```

```
```
Caso o pip não funcione:
```bash
python -m pip install pandas
```
📊 Sobre o Projeto
Projeto desenvolvido com foco na intersecção entre Ciências Contábeis, Administração e Engenharia de Dados, visando otimizar processos de Controladoria Multi-bancos.