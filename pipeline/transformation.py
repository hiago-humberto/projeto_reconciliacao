import pandas as pd

def higienizar_dados(df_bancos: pd.DataFrame) -> pd.DataFrame:
    regex = r'TED |PIX |DOC | - DUPLICADO'
    df_bancos['Cliente_Limpo'] = (
        df_bancos['Descricao_Banco']
        .fillna('')
        .str.replace(regex, '', regex=True)
        .str.strip()
        .str.upper()
    )
    return df_bancos