import pandas as pd

print("Iniciando o Motor de Reconciliação...\n")

# --- PASSO 1: EXTRAÇÃO (Lendo os dados gerados) ---
# O parâmetro sep=';' avisa ao Pandas como as colunas estão separadas no arquivo
df_sistema = pd.read_csv('sistema_financeiro.csv', sep=';')
df_banco = pd.read_csv('extrato_bancario.csv', sep=';')


# --- PASSO 2: LIMPEZA E PADRONIZAÇÃO (A mágica da Engenharia de Dados) ---

# 2.1 Convertendo Textos para Datas Reais
# O Pandas lê o CSV e acha que '2026-04-20' é só um pedaço de texto. 
# Precisamos transformar isso em um objeto de "Data" (datetime) para podermos fazer cálculos (ex: "pagou com 2 dias de atraso?")
df_sistema['Data_Emissao'] = pd.to_datetime(df_sistema['Data_Emissao'])
df_banco['Data_Compensacao'] = pd.to_datetime(df_banco['Data_Compensacao'])

# 2.2 Limpeza de Strings (Textos)
# Sistemas diferentes podem gravar "Empresa A " (com espaço no fim) ou "empresa a" (minúsculo).
# Vamos forçar tudo para MAIÚSCULO (.str.upper()) e remover espaços inúteis nas pontas (.str.strip())
df_sistema['Cliente'] = df_sistema['Cliente'].str.strip().str.upper()


# --- PASSO 3: VERIFICAÇÃO ---
# Vamos imprimir os "tipos" das colunas para provar que a limpeza funcionou
print("Tipos de dados no Sistema:")
print(df_sistema.dtypes)
print("\nPrimeiras linhas do Sistema:")
print(df_sistema.head())


# --- PASSO 3: O MOTOR DE CRUZAMENTO (A Reconciliação) ---

# 3.1 Criando uma "Chave" de ligação
# Vamos limpar a descrição do banco para isolar apenas o nome da empresa.
# Usamos o .str.replace() para trocar as palavras indesejadas por "nada" ('').
df_banco['Cliente_Extraido'] = df_banco['Descricao_Banco'].str.replace('TED ', '').str.replace('PIX ', '').str.replace('DOC ', '').str.replace(' - DUPLICADO', '')

# 3.2 O Cruzamento (O famoso JOIN)
# Juntamos a tabela do sistema com a do banco usando o nome do cliente como "ponte".
# how='left' garante que NENHUM registro do sistema financeiro seja perdido, mesmo que não achemos no banco.
df_cruzamento = pd.merge(df_sistema, df_banco, left_on='Cliente', right_on='Cliente_Extraido', how='left', validate='1:m') 

# 3.3 Tratando os "Buracos" (Valores Nulos)
# Se o cliente (como a Empresa C) não pagou, o valor do banco virá como NaN (Not a Number - vazio).
# A contabilidade não aceita "vazio". Vamos preencher esses vazios com 0.00.
df_cruzamento['Valor_Recebido'] = df_cruzamento['Valor_Recebido'].fillna(0)

# 3.4 A Regra de Negócio (Encontrando a Diferença)
df_cruzamento['Diferenca_R$'] = df_cruzamento['Valor_Esperado'] - df_cruzamento['Valor_Recebido']

print("\n--- RESULTADO DA AUDITORIA ---")
# Selecionamos apenas as colunas que importam para o diretor financeiro ver
resultado_visual = df_cruzamento[['Cliente', 'Valor_Esperado', 'Valor_Recebido', 'Diferenca_R$']]
print(resultado_visual)

# --- PASSO 4: GERAÇÃO DO RELATÓRIO (O Entregável) ---

# 4.1 Filtrando as Inconsistências
# O diretor só quer ver quem pagou a mais, a menos, ou não pagou. 
# Ou seja, onde a diferença é diferente (!=) de zero.
df_inconsistencias = resultado_visual[resultado_visual['Diferenca_R$'] != 0.0]

# 4.2 Exportando o Relatório de Auditoria
# Salvamos o resultado em um novo arquivo para a diretoria.
df_inconsistencias.to_csv('relatorio_excecoes_auditoria.csv', index=False, sep=';')

print(f"\n✅ Auditoria finalizada com sucesso!")
print(f"Foram encontradas {len(df_inconsistencias)} inconsistências.")
print("Relatório 'relatorio_excecoes_auditoria.csv' gerado na pasta.")