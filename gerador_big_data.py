import pandas as pd
import numpy as np
import random

print("Gerando Big Data... isso pode levar uns 10 segundos. Aguarde!")

# 1. CRIANDO 100 MIL COBRANÇAS (O ERP)
num_registros = 100000
clientes = [f"EMPRESA {i}" for i in range(1, num_registros + 1)]
# Gera valores aleatórios entre R$ 100 e R$ 5000
valores = np.round(np.random.uniform(100.0, 5000.0, num_registros), 2)

df_sistema = pd.DataFrame({
    'ID_Transacao': [f"SYS{i:06d}" for i in range(1, num_registros + 1)],
    'Data_Emissao': ['2026-04-28'] * num_registros,
    'Cliente': clientes,
    'Valor_Esperado': valores
})

# 2. CRIANDO OS PAGAMENTOS (Os Bancos)
# Vamos simular que 10 mil empresas NÃO pagaram (inadimplência)
indices_pagantes = random.sample(range(num_registros), 90000)

clientes_banco = []
valores_banco = []
bancos_nomes = []
descricoes = []

lista_bancos = ['Itaú', 'Bradesco', 'Santander', 'Banco do Brasil']
prefixos = ['PIX ', 'TED ', 'DOC ']

for i in indices_pagantes:
    cliente = clientes[i]
    valor_real = valores[i]
    
    # Injetando Caos: 5% dos clientes vão pagar com 50 centavos a menos (taxa)
    if random.random() < 0.05:
        valor_real = round(valor_real - 0.50, 2)
        
    clientes_banco.append(cliente)
    valores_banco.append(valor_real)
    bancos_nomes.append(random.choice(lista_bancos))
    descricoes.append(random.choice(prefixos) + cliente) # Sujeira no texto

df_bancos = pd.DataFrame({
    'Banco': bancos_nomes,
    'Data_Compensacao': ['2026-04-29'] * 90000,
    'Descricao_Banco': descricoes,
    'Valor_Recebido': valores_banco
})

# 3. EXPORTANDO OS ARQUIVOS GIGANTES
df_sistema.to_csv('sistema_big_data.csv', index=False, sep=';')

for banco in lista_bancos:
    df_temp = df_bancos[df_bancos['Banco'] == banco]
    nome_arquivo = f"extrato_{banco.lower().replace(' ', '_')}_big.csv"
    df_temp.to_csv(nome_arquivo, index=False, sep=';')

print("✅ Sucesso! Arquivos gigantes gerados na sua pasta.")