# 🔍 Motor de Reconciliação Financeira e Auditoria Automatizada

## 📌 O Problema de Negócio
Em auditorias contábeis e rotinas financeiras de grandes corporações, o cruzamento de dados entre o Sistema de Gestão (ERP) e os Extratos Bancários é frequentemente feito de forma manual ou via planilhas pesadas. Isso gera lentidão, alto risco de erro humano e dificuldade na identificação rápida de fraudes, pagamentos duplicados ou inadimplência.

## 💡 A Solução
Este projeto é um script de **Engenharia de Dados Financeiros** construído em Python que automatiza o processo de reconciliação. O motor extrai, limpa, padroniza e cruza as bases de dados (Sistema vs. Banco), identificando exceções e gerando um relatório final de auditoria em segundos.

### ⚙️ Funcionalidades Principais (Pipeline de Dados)
1. **Extração:** Leitura de arquivos `.csv` simulando exportações de sistemas ERP e bancos.
2. **Data Cleansing (Limpeza):** Conversão de strings para objetos `datetime` e padronização de textos (remoção de espaços e conversão para maiúsculas) para garantir a integridade do cruzamento.
3. **Transformação e Cruzamento:** Utilização da biblioteca `pandas` para realizar um `LEFT JOIN` (merge) entre as bases, isolando chaves de ligação a partir de descrições bancárias sujas.
4. **Regra de Negócio:** Tratamento de valores nulos (`NaN` para `0.00`) para preservar a matemática do balanço e cálculo automático de discrepâncias.
5. **Carga (Relatório):** Filtro inteligente que ignora transações corretas e exporta um arquivo `.csv` isolando apenas as inconsistências (pagamentos duplicados, a menor, a maior ou não realizados).

## 🛠️ Tecnologias Utilizadas
* **Python 3.x:** Linguagem base para automação.
* **Pandas:** Biblioteca principal para manipulação, limpeza e análise de grandes volumes de dados tabulares.

## 🚀 Como Executar o Projeto

1. Clone este repositório:
   ```bash
   git clone [https://github.com/seu-usuario/projeto_reconciliacao.git](https://github.com/seu-usuario/projeto_reconciliacao.git)