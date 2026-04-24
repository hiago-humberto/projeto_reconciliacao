import pandas as pd

# 1. Dados do Sistema Financeiro (ERP TOTVS)
dados_sistema = {
    'ID_Transacao': ['SYS001', 'SYS002', 'SYS003', 'SYS004', 'SYS005'],
    'Data_Emissao': ['2026-04-20', '2026-04-21', '2026-04-22', '2026-04-23', '2026-04-24'],
    'Cliente': ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa D', 'Empresa E'],
    'Valor_Esperado': [1500.00, 3250.50, 800.00, 4100.00, 950.00]
}

# 2. Extrato do ITAÚ (Alguns clientes pagaram aqui)
dados_itau = {
    'Banco': ['Itaú', 'Itaú'],
    'Data_Compensacao': ['2026-04-21', '2026-04-24'],
    'Descricao_Banco': ['TED EMPRESA A', 'PIX EMPRESA E'],
    'Valor_Recebido': [1500.00, 950.00] 
}

# 3. Extrato do BRADESCO (Outros pagaram aqui, e com erros)
dados_bradesco = {
    'Banco': ['Bradesco', 'Bradesco', 'Bradesco'],
    'Data_Compensacao': ['2026-04-22', '2026-04-24', '2026-04-24'],
    'Descricao_Banco': ['PIX EMPRESA B', 'DOC EMPRESA D', 'PIX EMPRESA D - DUPLICADO'],
    'Valor_Recebido': [3250.00, 4100.00, 4100.00] 
}

# Transformando em Tabelas (DataFrames)
df_sistema = pd.DataFrame(dados_sistema)
df_itau = pd.DataFrame(dados_itau)
df_bradesco = pd.DataFrame(dados_bradesco)

# Exportando os 3 arquivos
df_sistema.to_csv('sistema_financeiro.csv', index=False, sep=';')
df_itau.to_csv('extrato_itau.csv', index=False, sep=';')
df_bradesco.to_csv('extrato_bradesco.csv', index=False, sep=';')

print("Arquivos gerados: sistema_financeiro.csv, extrato_itau.csv e extrato_bradesco.csv")