from typing import List, Tuple, IO
import pandas as pd
import logging

from pipeline.ingestion import extrair_e_validar_dados
from pipeline.transformation import higienizar_dados
from pipeline.audit import auditar_transacoes
from pipeline.datalake import gerenciar_data_lake

def orquestrar_pipeline_auditoria(arquivo_erp: IO, arquivos_bancos: List[IO], limite_fraude: float) -> Tuple[pd.DataFrame, int, int]:
    logging.info("--- INICIANDO PIPELINE DE AUDITORIA ---")
    
    df_erp, df_bancos_brutos = extrair_e_validar_dados(arquivo_erp, arquivos_bancos)
    df_bancos_limpos = higienizar_dados(df_bancos_brutos)
    df_final = auditar_transacoes(df_erp, df_bancos_limpos, limite_fraude)
    
    gerenciar_data_lake(df_erp, df_bancos_brutos, df_final)
    
    logging.info("--- PIPELINE CONCLUÍDO COM SUCESSO ---")
    return df_final, len(df_erp), len(df_bancos_brutos)