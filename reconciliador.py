import pandas as pd
import numpy as np

print("Iniciando o Motor de Reconciliação Multi-Bancos...\n")

# --- PASSO 1: EXTRAÇÃO MULTI-FONTES ---
df_sistema = pd.read_csv('sistema_financeiro.csv', sep=';')
df_itau = pd.read_csv('extrato_itau.csv', sep=';')
df_bradesco = pd.read_csv('extrato_bradesco.csv', sep=';')

# 💡 A MÁGICA ACONTECE AQUI: Empilhando os extratos
# O ignore_index=True refaz a numeração das linhas para não dar conflito.
df_banco_consolidado = pd.concat([df_itau, df_bradesco], ignore_index=True)

# --- PASSO 2: LIMPEZA ---
df_sistema['Cliente'] = df_sistema['Cliente'].str.strip().str.upper()

# Limpando o Super Extrato
df_banco_consolidado['Cliente_Extraido'] = df_banco_consolidado['Descricao_Banco'].str.replace('TED ', '').str.replace('PIX ', '').str.replace('DOC ', '').str.replace(' - DUPLICADO', '')

# --- PASSO 3: O CRUZAMENTO ---
df_cruzamento = pd.merge(df_sistema, df_banco_consolidado, left_on='Cliente', right_on='Cliente_Extraido', how='left', validate='1:m')

df_cruzamento['Valor_Recebido'] = df_cruzamento['Valor_Recebido'].fillna(0)
df_cruzamento['Diferenca_R$'] = df_cruzamento['Valor_Esperado'] - df_cruzamento['Valor_Recebido']
# Se o cliente não pagou, preenchemos o nome do Banco com 'Não Localizado'
df_cruzamento['Banco'] = df_cruzamento['Banco'].fillna('Não Localizado')

# --- PASSO 4: CLASSIFICAÇÃO INTELIGENTE (STATUS) ---
condicoes = [
    (df_cruzamento['Diferenca_R$'] == 0),
    (df_cruzamento['Diferenca_R$'] > 0),
    (df_cruzamento['Diferenca_R$'] < 0)
]
status = ['Conciliado (OK)', 'Pendente / Parcial', 'Duplicado / A Maior']
df_cruzamento['Status'] = np.select(condicoes, status, default='Erro')

# --- RESULTADO FINAL ---
print("--- RELATÓRIO DE AUDITORIA CONSOLIDADO ---")
# Agora incluímos a coluna Banco para o diretor saber de onde veio o dinheiro
resultado_visual = df_cruzamento[['Cliente', 'Banco', 'Valor_Esperado', 'Valor_Recebido', 'Diferenca_R$', 'Status']]
print(resultado_visual)

# Salvando o relatório de exceções (filtrando quem NÃO está OK)
df_inconsistencias = resultado_visual[resultado_visual['Status'] != 'Conciliado (OK)']
df_inconsistencias.to_csv('relatorio_excecoes_auditoria.csv', index=False, sep=';')
print(f"\n✅ Relatório gerado! Foram encontradas {len(df_inconsistencias)} exceções de auditoria.")