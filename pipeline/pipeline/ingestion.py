import pandas as pd
import logging
from typing import List, Tuple, IO

def validar_schema_e_conteudo(df: pd.DataFrame, colunas_obrigatorias: List[str], nome_fonte: str) -> None:
    colunas_atuais = [c.strip().upper() for c in df.columns]
    colunas_faltantes = [c for c in colunas_obrigatorias if c.upper() not in colunas_atuais]
    
    if colunas_faltantes:
        msg_erro = f"Falha de Schema no '{nome_fonte}'. Faltam as colunas: {colunas_faltantes}"
        logging.error(msg_erro)
        raise ValueError(msg_erro)

    colunas_valor = [c for c in df.columns if 'VALOR' in c.upper()]
    for col in colunas_valor:
        valores_numericos = pd.to_numeric(df[col], errors='coerce')
        if (valores_numericos < 0).any():
            msg_erro = f"Falha: Valores negativos não permitidos na coluna '{col}' do '{nome_fonte}'."
            logging.error(msg_erro)
            raise ValueError(msg_erro)

def extrair_e_validar_dados(arquivo_erp: IO, arquivos_bancos: List[IO]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    logging.info("Iniciando extração...")
    
    df_sistema = pd.read_csv(arquivo_erp, sep=';')
    validar_schema_e_conteudo(df_sistema, ['Cliente', 'Valor_Esperado'], "Sistema ERP")
    df_sistema['Cliente'] = df_sistema['Cliente'].str.strip().str.upper()
    
    lista_dfs = [pd.read_csv(f, sep=';') for f in arquivos_bancos]
    df_bancos = pd.concat(lista_dfs, ignore_index=True)
    validar_schema_e_conteudo(df_bancos, ['Descricao_Banco', 'Valor_Recebido', 'Banco'], "Extratos Bancários")
    
    return df_sistema, df_bancos