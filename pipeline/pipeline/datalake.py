import pandas as pd
import os
import time
import logging

def gerar_path(camada: str, prefixo: str) -> str:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    pasta = f"data/{camada}"
    os.makedirs(pasta, exist_ok=True)
    return f"{pasta}/{prefixo}_{timestamp}.parquet"

def gerenciar_data_lake(df_erp: pd.DataFrame, df_bancos_brutos: pd.DataFrame, df_final: pd.DataFrame) -> None:
    logging.info("Salvando nas camadas RAW e PROCESSED do Data Lake...")
    df_erp.to_parquet(gerar_path("raw", "erp"), index=False)
    df_bancos_brutos.to_parquet(gerar_path("raw", "bancos"), index=False)
    df_final.to_parquet(gerar_path("processed", "reconciliado"), index=False)