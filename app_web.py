import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import logging
import os
from typing import List, Tuple

# --- CONFIGURAÇÃO DO LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [MOTOR_ETL] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- 1. CONFIGURAÇÃO DE INTERFACE E FLUXO VISUAL ---
st.set_page_config(page_title="Audit Intelligence Hub", page_icon="🛡️", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #0D47A1;'>🛡️ Audit Intelligence Hub</h1>
    <p style='text-align: center; color: #555; font-size: 1.2em;'>Pipeline Desacoplado & Data Lake (Enterprise Grade)</p>
""", unsafe_allow_html=True)

# O FLUXO VISUAL VOLTOU AQUI
st.markdown("""
<div style='text-align: center; margin-top: 10px; margin-bottom: 30px;'>
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>📤 1. Upload</span> ➔ 
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>🛡️ 2. Validação</span> ➔ 
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>⚙️ 3. Motor ETL</span> ➔ 
    <span style='background-color: #1565c0; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: white;'>📊 4. Insights</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- 2. CAMADA DE DADOS E NEGÓCIOS (Totalmente Desacoplada do Streamlit) ---

def validar_schema(df: pd.DataFrame, colunas_obrigatorias: List[str], nome_fonte: str) -> None:
    colunas_atuais = [c.strip().upper() for c in df.columns]
    colunas_faltantes = [c for c in colunas_obrigatorias if c.upper() not in colunas_atuais]
    
    if colunas_faltantes:
        msg_erro = f"Falha de Schema no arquivo '{nome_fonte}'. Faltam as colunas: {colunas_faltantes}"
        logging.error(msg_erro)
        raise ValueError(msg_erro)

@st.cache_data(show_spinner=False)
def extrair_e_validar_dados(arquivo_erp, arquivos_bancos: List) -> Tuple[pd.DataFrame, pd.DataFrame]:
    logging.info("Iniciando extração...")
    df_sistema = pd.read_csv(arquivo_erp, sep=';')
    validar_schema(df_sistema, ['Cliente', 'Valor_Esperado'], "Sistema ERP")
    df_sistema['Cliente'] = df_sistema['Cliente'].str.strip().str.upper()
    
    lista_dfs = [pd.read_csv(f, sep=';') for f in arquivos_bancos]
    df_bancos = pd.concat(lista_dfs, ignore_index=True)
    validar_schema(df_bancos, ['Descricao_Banco', 'Valor_Recebido', 'Banco'], "Extratos Bancários")
    
    return df_sistema, df_bancos

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

def auditar_transacoes(df_sistema: pd.DataFrame, df_bancos: pd.DataFrame, limite_fraude: float) -> pd.DataFrame:
    df_bancos['Valor_Recebido'] = df_bancos['Valor_Recebido'].fillna(0)
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

def gerenciar_data_lake(df_erp: pd.DataFrame, df_bancos_brutos: pd.DataFrame, df_final: pd.DataFrame) -> None:
    logging.info("Salvando nas camadas RAW e PROCESSED do Data Lake...")
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    df_erp.to_parquet(f"data/raw/erp_raw_{timestamp}.parquet", index=False)
    df_bancos_brutos.to_parquet(f"data/raw/bancos_raw_{timestamp}.parquet", index=False)
    df_final.to_parquet(f"data/processed/reconciliado_{timestamp}.parquet", index=False)

# --- 3. O ORQUESTRADOR ---

def orquestrar_pipeline_auditoria(arquivo_erp, arquivos_bancos, limite_fraude) -> Tuple[pd.DataFrame, int, int]:
    df_erp, df_bancos_brutos = extrair_e_validar_dados(arquivo_erp, arquivos_bancos)
    df_bancos_limpos = higienizar_dados(df_bancos_brutos)
    df_final = auditar_transacoes(df_erp, df_bancos_limpos, limite_fraude)
    
    gerenciar_data_lake(df_erp, df_bancos_brutos, df_final)
    
    return df_final, len(df_erp), len(df_bancos_brutos)


# --- 4. ÁREA DE INPUTS (FRONTEND / VIEW) ---
with st.sidebar:
    st.header("⚙️ Configurações do Motor")
    default_outlier = int(os.getenv("DEFAULT_OUTLIER_LIMIT", 5000))
    limite_outlier = st.slider("Sensibilidade de Outlier (R$)", 0, 20000, default_outlier)
    st.info("O motor marcará como 'Suspeito' qualquer valor recebido acima deste limite que não esteja no ERP.")

# O EXPLICADOR CURTO VOLTOU AQUI, ANTES DOS UPLOADS
st.markdown("### 📥 Ingestão de Dados")
st.markdown("*Faça upload do ERP e extratos bancários para identificar divergências automaticamente.*")

col1, col2 = st.columns([1, 2])
with col1:
    arq_sistema = st.file_uploader("Relatório de Contas a Receber (ERP)", type=['csv'])
with col2:
    arq_bancos = st.file_uploader("Extratos Bancários (Arraste múltiplos arquivos)", type=['csv'], accept_multiple_files=True)


# --- 5. EXECUÇÃO (CONTROLLER) ---
if st.button("🚀 INICIAR AUDITORIA INTELIGENTE", use_container_width=True):
    if arq_sistema and arq_bancos:
        start_time = time.time()
        
        with st.spinner("Executando pipeline de dados..."):
            try:
                df_final, qtd_erp, qtd_bancos = orquestrar_pipeline_auditoria(arq_sistema, arq_bancos, limite_outlier)
                
            except ValueError as ve:
                st.error(f"⚠️ Erro de Validação: {str(ve)}")
                st.stop()
            except Exception as e:
                st.error(f"🚨 Erro Crítico do Sistema: {str(e)}")
                st.stop()
            
            exec_duration = time.time() - start_time

            # --- RENDERIZAÇÃO VISUAL ---
            st.toast("Protocolo finalizado com sucesso!")
            
            log_col1, log_col2, log_col3, log_col4 = st.columns(4)
            log_col1.metric("Registros ERP", qtd_erp)
            log_col2.metric("Registros Bancários", qtd_bancos)
            log_col3.metric("Tempo de Execução", f"{exec_duration:.4f}s")
            log_col4.metric("Alertas de Risco", len(df_final[df_final['Alerta_Fraude'] == "🚩 SUSPEITO"]))

            st.divider()
            st.markdown("### 💰 Visão Executiva Financeira")
            
            total_esperado = df_final['Valor_Esperado'].sum()
            total_recebido = df_final['Valor_Recebido'].sum()
            total_pendente = df_final.loc[df_final['Diferenca'] > 0, 'Diferenca'].sum()
            
            fin_col1, fin_col2, fin_col3 = st.columns(3)
            fin_col1.metric("Total Esperado (ERP)", f"R$ {total_esperado:,.2f}")
            fin_col2.metric("Total Conciliado (Bancos)", f"R$ {total_recebido:,.2f}")
            fin_col3.metric("Risco de Inadimplência", f"R$ {total_pendente:,.2f}", delta="- Furo de Caixa", delta_color="inverse")
            st.divider()

            c1, c2 = st.columns(2)
            with c1:
                df_fraudes = df_final[df_final['Alerta_Fraude'] == "🚩 SUSPEITO"]
                if not df_fraudes.empty:
                    fig_status = px.pie(df_fraudes, values='Valor_Recebido', names='Banco', hole=0.5,
                                        title="⚠️ Concentração do Volume Suspeito por Banco",
                                        color_discrete_sequence=px.colors.sequential.Reds_r)
                    fig_status.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_status, use_container_width=True)
                else:
                    st.success("🎉 Nenhuma fraude ou anomalia detectada nos bancos!")

            with c2:
                st.markdown("### 🔥 Top Alertas de Risco")
                df_risco = df_final[df_final['Alerta_Fraude'] == "🚩 SUSPEITO"].nlargest(5, 'Valor_Recebido')
                if not df_risco.empty:
                    st.table(df_risco[['Cliente', 'Banco', 'Valor_Recebido', 'Alerta_Fraude']])
                else:
                    st.success("Nenhuma transação suspeita detectada.")
            st.divider()

            st.markdown("### 📋 Relatório Consolidado")
            st.dataframe(df_final, use_container_width=True)
            
            csv_data = df_final.to_csv(index=False, sep=';').encode('utf-8')
            st.download_button(
                label="📥 Baixar Relatório",
                data=csv_data,
                file_name=f"auditoria_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("Aguardando upload dos arquivos para iniciar o protocolo de segurança.")