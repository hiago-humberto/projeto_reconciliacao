import pandas as pd
import random

# 1. Dados do Sistema Financeiro (ERP)
dados_sistema = {
    'ID_Transacao': ['SYS001', 'SYS002', 'SYS003', 'SYS004', 'SYS005'],
    'Data_Emissao': ['2026-04-20', '2026-04-21', '2026-04-22', '2026-04-23', '2026-04-24'],
    'Cliente': ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa D', 'Empresa E'],
    'Valor_Esperado': [1500.00, 3250.50, 800.00, 4100.00, 950.00],
    'Status': ['Aberto', 'Aberto', 'Aberto', 'Aberto', 'Aberto']
}

# 2. Dados do Extrato Bancário (O que realmente caiu na conta)
dados_banco = {
    'Data_Compensacao': ['2026-04-21', '2026-04-22', '2026-04-24', '2026-04-24'],
    'Descricao_Banco': ['TED EMPRESA A', 'PIX EMPRESA B', 'DOC EMPRESA D', 'PIX EMPRESA D - DUPLICADO'],
    'Valor_Recebido': [1500.00, 3250.00, 4100.00, 4100.00] 
}

# Criando os DataFrames (tabelas virtuais)
df_sistema = pd.DataFrame(dados_sistema)
df_banco = pd.DataFrame(dados_banco)

# Exportando para arquivos CSV na sua pasta
df_sistema.to_csv('sistema_financeiro.csv', index=False, sep=';')
df_banco.to_csv('extrato_bancario.csv', index=False, sep=';')

print("Arquivos 'sistema_financeiro.csv' e 'extrato_bancario.csv' gerados com sucesso!")