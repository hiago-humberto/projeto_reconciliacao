import streamlit as st
import plotly.express as px
import time
import logging
import os

# 🟢 OLHA A MÁGICA AQUI: Nós importamos apenas o orquestrador do nosso próprio pacote!
from pipeline.orchestrator import orquestrar_pipeline_auditoria

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

st.set_page_config(page_title="Audit Intelligence Hub", page_icon="🛡️", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #0D47A1;'>🛡️ Audit Intelligence Hub</h1>
    <p style='text-align: center; color: #555; font-size: 1.2em;'>Automação de Reconciliação Bancária e Prevenção de Perdas</p>
""", unsafe_allow_html=True)

st.divider()

with st.sidebar:
    st.header("⚙️ Configurações do Motor")
    default_outlier = int(os.getenv("DEFAULT_OUTLIER_LIMIT", 5000))
    limite_outlier = st.slider("Sensibilidade de Outlier (R$)", 0, 20000, default_outlier)
    st.info("O motor marcará como 'Suspeito' qualquer valor recebido acima deste limite que não esteja no ERP.")

st.markdown("### 📥 Ingestão de Dados")
st.markdown("*Faça upload do ERP e extratos bancários para identificar divergências automaticamente.*")

col1, col2 = st.columns([1, 2])
with col1:
    arq_sistema = st.file_uploader("Relatório de Contas a Receber (ERP)", type=['csv'])
with col2:
    arq_bancos = st.file_uploader("Extratos Bancários (Arraste múltiplos arquivos)", type=['csv'], accept_multiple_files=True)

if st.button("🚀 INICIAR AUDITORIA INTELIGENTE", use_container_width=True):
    if arq_sistema and arq_bancos:
        start_time = time.time()
        with st.spinner("Executando pipeline de dados..."):
            try:
                # O Controller chama a lógica de negócios isolada
                df_final, qtd_erp, qtd_bancos = orquestrar_pipeline_auditoria(arq_sistema, arq_bancos, limite_outlier)
            except ValueError as ve:
                st.error(f"⚠️ Erro de Validação: {str(ve)}")
                st.stop()
            except Exception as e:
                st.error(f"🚨 Erro Crítico: {str(e)}")
                st.stop()
            
            exec_duration = time.time() - start_time

            st.toast("Protocolo finalizado com sucesso!")
            
            # --- RENDERIZAÇÃO DAS MÉTRICAS ---
            log_col1, log_col2, log_col3, log_col4 = st.columns(4)
            log_col1.metric("Registros ERP", qtd_erp)
            log_col2.metric("Registros Bancários", qtd_bancos)
            log_col3.metric("Tempo de Execução", f"{exec_duration:.4f}s")
            log_col4.metric("Alertas de Risco", len(df_final[df_final['Alerta_Fraude'] == "🚩 SUSPEITO"]))

            st.divider()
            
            # (Aqui você mantém exatamente a mesma parte do código que renderiza as tabelas, gráficos de pizza e o botão de download... cortei aqui só para não ficar gigantesca a mensagem, mas a lógica visual é idêntica!)