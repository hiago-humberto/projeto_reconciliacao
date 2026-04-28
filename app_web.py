import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# --- 1. CONFIGURAÇÃO DE INTERFACE ---
st.set_page_config(page_title="Audit Intelligence Hub", page_icon="🛡️", layout="wide")

# Estilização do Header
st.markdown("""
    <h1 style='text-align: center; color: #0D47A1;'>🛡️ Audit Intelligence Hub</h1>
    <p style='text-align: center; color: #555; font-size: 1.2em;'>Detecção de Fraudes, Reconciliação Multi-Bancos e Insights Preditivos</p>
""", unsafe_allow_html=True)

# 👇 O FLUXO VISUAL RETORNOU AQUI 👇
st.markdown("""
<div style='text-align: center; margin-top: 10px; margin-bottom: 30px;'>
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>📤 1. Upload</span> ➔ 
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>⚙️ 2. Processamento</span> ➔ 
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>🛡️ 3. Auditoria</span> ➔ 
    <span style='background-color: #1565c0; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: white;'>📊 4. Insights</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- 2. ÁREA DE INPUTS ---
with st.sidebar:
    st.header("⚙️ Configurações do Motor")
    limite_outlier = st.slider("Sensibilidade de Outlier (R$)", 0, 20000, 5000)
    st.info("O motor marcará como 'Suspeito' qualquer valor recebido acima deste limite que não esteja no ERP.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📤 Fonte de Dados ERP")
    arq_sistema = st.file_uploader("Relatório de Contas a Receber", type=['csv'])

with col2:
    st.subheader("📤 Extratos Bancários (Múltiplos)")
    arq_bancos = st.file_uploader("Arraste todos os arquivos de uma vez", type=['csv'], accept_multiple_files=True)

# --- 3. PROCESSAMENTO COM WOW FEATURES ---
if st.button("🚀 INICIAR AUDITORIA INTELIGENTE", use_container_width=True):
    if arq_sistema and arq_bancos:
        start_time = time.time() # Início do cronômetro
        
        with st.spinner("Executando protocolos de auditoria..."):
            
            # --- LÓGICA DE CARREGAMENTO E HIGIENIZAÇÃO ---
            df_sistema = pd.read_csv(arq_sistema, sep=';')
            df_sistema['Cliente'] = df_sistema['Cliente'].str.strip().str.upper()
            
            # Empilhamento Dinâmico
            lista_dfs = [pd.read_csv(f, sep=';') for f in arq_bancos]
            df_bancos = pd.concat(lista_dfs, ignore_index=True)
            
            # Higienização de nomenclaturas bancárias
            df_bancos['Cliente_Limpo'] = df_bancos['Descricao_Banco'].str.replace(r'TED |PIX |DOC | - DUPLICADO', '', regex=True)
            
            # --- DETECÇÃO DE FRAUDES E CRUZAMENTO ---
            df_bancos['Eh_Duplicado'] = df_bancos.duplicated(subset=['Cliente_Limpo', 'Valor_Recebido', 'Banco'], keep=False)
            df_final = pd.merge(df_sistema, df_bancos, left_on='Cliente', right_on='Cliente_Limpo', how='left')
            
            # Tratamento de Nulos
            df_final['Valor_Recebido'] = df_final['Valor_Recebido'].fillna(0)
            df_final['Banco'] = df_final['Banco'].fillna('Não Localizado')
            df_final['Diferenca'] = df_final['Valor_Esperado'] - df_final['Valor_Recebido']
            
            # Identificar Outliers e Fraudes
            df_final['Alerta_Fraude'] = np.where(
                (df_final['Eh_Duplicado'] == True) | (df_final['Valor_Recebido'] > limite_outlier),
                "🚩 SUSPEITO", "✅ NORMAL"
            )

            end_time = time.time()
            exec_duration = end_time - start_time

            # --- 4. LOG DE AUDITORIA ---
            st.toast("Processamento concluído!")
            log_col1, log_col2, log_col3, log_col4 = st.columns(4)
            log_col1.metric("Registros ERP", len(df_sistema))
            log_col2.metric("Registros Bancários", len(df_bancos))
            log_col3.metric("Tempo de Execução", f"{exec_duration:.4f}s")
            log_col4.metric("Alertas de Risco", len(df_final[df_final['Alerta_Fraude'] == "🚩 SUSPEITO"]))

            st.divider()

            # --- VISÃO EXECUTIVA FINANCEIRA ---
            st.markdown("### 💰 Visão Executiva Financeira")
            
            total_esperado = df_final['Valor_Esperado'].sum()
            total_recebido = df_final['Valor_Recebido'].sum()
            total_pendente = df_final.loc[df_final['Diferenca'] > 0, 'Diferenca'].sum()
            
            fin_col1, fin_col2, fin_col3 = st.columns(3)
            fin_col1.metric("Total Esperado (ERP)", f"R$ {total_esperado:,.2f}")
            fin_col2.metric("Total Conciliado (Bancos)", f"R$ {total_recebido:,.2f}")
            fin_col3.metric("Risco de Inadimplência", f"R$ {total_pendente:,.2f}", delta="- Furo de Caixa", delta_color="inverse")

            st.divider()

            # --- 5. DASHBOARD DE INSIGHTS ---
            c1, c2 = st.columns(2)
            
            with c1:
                # 👇 O NOVO GRÁFICO DE INSIGHT DE MERCADO 👇
                # Filtramos apenas as transações suspeitas para ver ONDE a fraude mora
                df_fraudes = df_final[df_final['Alerta_Fraude'] == "🚩 SUSPEITO"]
                
                if not df_fraudes.empty:
                    fig_status = px.pie(df_fraudes, values='Valor_Recebido', names='Banco', hole=0.5,
                                        title="⚠️ Concentração do Volume Suspeito por Banco",
                                        color_discrete_sequence=px.colors.sequential.Reds_r)
                    
                    # Força o gráfico a mostrar a Porcentagem e o Nome do Banco direto na imagem
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
                    st.success("Nenhuma transação suspeita detectada neste lote.")

            st.divider()

            # --- 6. EXPORTAÇÃO INTELIGENTE ---
            st.markdown("### 📋 Relatório Consolidado")
            st.dataframe(df_final, use_container_width=True)
            
            csv_data = df_final.to_csv(index=False, sep=';').encode('utf-8')
            st.download_button(
                label="📥 Baixar Relatório de Auditoria para Excel",
                data=csv_data,
                file_name=f"auditoria_final_{time.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("Aguardando upload dos arquivos para iniciar o protocolo de segurança.")