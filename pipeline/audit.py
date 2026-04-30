import pandas as pd
import numpy as np

def auditar_transacoes(df_sistema: pd.DataFrame, df_bancos: pd.DataFrame, limite_fraude: float) -> pd.DataFrame:
    df_bancos['Valor_Recebido'] = pd.to_numeric(df_bancos['Valor_Recebido'], errors='coerce').fillna(0)
    df_bancos['Eh_Duplicado'] = df_bancos.duplicated(subset=['Cliente_Limpo', 'Valor_Recebido', 'Banco'], keep=False)
    
    df_final = pd.merge(df_sistema, df_bancos, left_on='Cliente', right_on='Cliente_Limpo', how='left')
    df_final['Valor_Recebido'] = df_final['Valor_Recebido'].fillna(0)
    df_final['Banco'] = df_final['Banco'].fillna('Não Localizado')
    df_final['Diferenca'] = df_final['Valor_Esperado'] - df_final['Valor_Recebido']
    
    df_final['Alerta_Fraude'] = np.where(
        (df_final['Eh_Duplicado'] == True) | (df_final['Valor_Recebido'] > limite_fraude),
        "🚩 SUSPEITO", "✅ NORMAL"
    )
    return df_final