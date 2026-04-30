import streamlit as st
import plotly.express as px
import time
import logging
import os

# Importando a nossa regra de negócios isolada!
from pipeline.orchestrator import orquestrar_pipeline_auditoria

# Configuração do Log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- 1. CONFIGURAÇÃO DE INTERFACE E FLUXO VISUAL ---
st.set_page_config(page_title="Audit Intelligence Hub", page_icon="🛡️", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #0D47A1;'>🛡️ Audit Intelligence Hub</h1>
    <p style='text-align: center; color: #555; font-size: 1.2em;'>Automação de Reconciliação Bancária e Prevenção de Perdas</p>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin-top: 10px; margin-bottom: 30px;'>
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>📤 1. Upload</span> ➔ 
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>🛡️ 2. Validação</span> ➔ 
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>⚙️ 3. Motor ETL</span> ➔ 
    <span style='background-color: #1565c0; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: white;'>📊 4. Insights</span>
</div>
""", unsafe_allow_html=True)
st.divider()

# --- 2. ÁREA DE INPUTS (VIEW) ---
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

# --- 3. EXECUÇÃO (CONTROLLER) ---
if st.button("🚀 INICIAR AUDITORIA INTELIGENTE", use_container_width=True):
    if arq_sistema and arq_bancos:
        start_time = time.time()
        
        with st.spinner("Executando pipeline de dados..."):
            try:
                # O Controller chama a lógica de negócios isolada da pasta pipeline
                df_final, qtd_erp, qtd_bancos = orquestrar_pipeline_auditoria(arq_sistema, arq_bancos, limite_outlier)
                
            except ValueError as ve:
                st.error(f"⚠️ Erro de Validação: {str(ve)}")
                st.stop()
            except Exception as e:
                st.error(f"🚨 Erro Crítico do Sistema: {str(e)}")
                st.stop()
            
            exec_duration = time.time() - start_time

            # --- 4. RENDERIZAÇÃO VISUAL DOS RESULTADOS ---
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
                label="📥 Baixar Relatório Completo",
                data=csv_data,
                file_name=f"auditoria_final_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("Aguardando upload dos arquivos para iniciar o protocolo de segurança.")