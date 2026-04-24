import pandas as pd
import numpy as np

# 1. SETOR DE EXTRAÇÃO
def extrair_dados():
    """Lê os arquivos CSV e os transforma em DataFrames."""
    df_sistema = pd.read_csv('sistema_financeiro.csv', sep=';')
    df_itau = pd.read_csv('extrato_itau.csv', sep=';')
    df_bradesco = pd.read_csv('extrato_bradesco.csv', sep=';')
    
    return df_sistema, df_itau, df_bradesco

# 2. SETOR DE LIMPEZA E PREPARAÇÃO
def preparar_bancos(df_itau, df_bradesco):
    """Empilha os bancos e limpa as descrições para criar a chave de cruzamento."""
    df_banco_consolidado = pd.concat([df_itau, df_bradesco], ignore_index=True)
    
    # Limpeza de strings
    lixo_bancario = ['TED ', 'PIX ', 'DOC ', ' - DUPLICADO']
    df_banco_consolidado['Cliente_Extraido'] = df_banco_consolidado['Descricao_Banco']
    
    for lixo in lixo_bancario:
        df_banco_consolidado['Cliente_Extraido'] = df_banco_consolidado['Cliente_Extraido'].str.replace(lixo, '')
        
    return df_banco_consolidado

# 3. SETOR DE CRUZAMENTO (O MOTOR)
def cruzar_bases(df_sistema, df_banco_consolidado):
    """Cruza o ERP com os Bancos e calcula as diferenças."""
    df_sistema['Cliente'] = df_sistema['Cliente'].str.strip().str.upper()
    
    df_cruzamento = pd.merge(df_sistema, df_banco_consolidado, left_on='Cliente', right_on='Cliente_Extraido', how='left', validate='1:m')
    
    # Tratamento matemático
    df_cruzamento['Valor_Recebido'] = df_cruzamento['Valor_Recebido'].fillna(0)
    df_cruzamento['Banco'] = df_cruzamento['Banco'].fillna('Não Localizado')
    df_cruzamento['Diferenca_R$'] = df_cruzamento['Valor_Esperado'] - df_cruzamento['Valor_Recebido']
    
    return df_cruzamento

# 4. SETOR DE INTELIGÊNCIA E RELATÓRIO
def gerar_relatorio_auditoria(df_cruzamento):
    """Aplica as regras de negócio de Status e salva o CSV."""
    condicoes = [
        (df_cruzamento['Diferenca_R$'] == 0),
        (df_cruzamento['Diferenca_R$'] > 0),
        (df_cruzamento['Diferenca_R$'] < 0)
    ]
    status = ['Conciliado (OK)', 'Pendente / Parcial', 'Duplicado / A Maior']
    df_cruzamento['Status'] = np.select(condicoes, status, default='Erro')
    
    resultado_visual = df_cruzamento[['Cliente', 'Banco', 'Valor_Esperado', 'Valor_Recebido', 'Diferenca_R$', 'Status']]
    
    # Exportar apenas as exceções
    df_inconsistencias = resultado_visual[resultado_visual['Status'] != 'Conciliado (OK)']
    df_inconsistencias.to_csv('relatorio_excecoes_auditoria.csv', index=False, sep=';')
    
    return resultado_visual, len(df_inconsistencias)

# ==========================================
# O "GERENTE" DA FÁBRICA (Onde a mágica acontece)
# ==========================================
def main():
    print("Iniciando o Motor de Reconciliação Clean Architecture...\n")
    
    # O fluxo de trabalho fica visível e lógico:
    sistema, itau, bradesco = extrair_dados()
    bancos_prontos = preparar_bancos(itau, bradesco)
    cruzamento = cruzar_bases(sistema, bancos_prontos)
    relatorio_final, total_erros = gerar_relatorio_auditoria(cruzamento)
    
    print(relatorio_final)
    print(f"\n✅ Concluído! {total_erros} exceções encontradas e salvas no relatório.")

# Isso garante que o código só rode se você executar este arquivo diretamente
if __name__ == "__main__":
    main()