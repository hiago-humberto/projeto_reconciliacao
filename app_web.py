import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. CONFIGURAÇÃO E STORYTELLING VISUAL ---
st.set_page_config(page_title="Motor de Reconciliação Enterprise", page_icon="🚀", layout="wide")

# Header Forte
st.markdown("<h1 style='text-align: center; color: #1565c0;'>🚀 Motor de Reconciliação Bancária Automatizada</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>Auditoria financeira em milissegundos. Transforme dados caóticos em insights claros.</h4>", unsafe_allow_html=True)

# Fluxo Visual (Pipeline)
st.markdown("""
<div style='text-align: center; margin-top: 20px; margin-bottom: 30px;'>
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>📤 1. Upload</span> ➔ 
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>⚙️ 2. Processamento</span> ➔ 
    <span style='background-color: #e3f2fd; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: #1565c0;'>🛡️ 3. Validação</span> ➔ 
    <span style='background-color: #1565c0; padding: 10px 20px; border-radius: 20px; font-weight: bold; color: white;'>📊 4. Insights</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- 2. FUNÇÃO DE ROBUSTEZ (VALIDAÇÃO DE SCHEMA) ---
def validar_schema(df, colunas_esperadas, nome_arquivo):
    """Verifica se o arquivo enviado tem as colunas mínimas necessárias."""
    colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
    if colunas_faltantes:
        st.error(f"🚨 **Erro de Validação no arquivo '{nome_arquivo}':** Faltam as colunas {colunas_faltantes}. Verifique o padrão de exportação.")
        return False
    return True

# --- 3. UPLOAD DE ARQUIVOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🖥️ Sistema ERP (TOTVS/SAP)")
    st.caption("Faça o upload do relatório de 'Contas a Receber'.")
    arq_sistema = st.file_uploader("Arquivo do Sistema (.csv)", type=['csv'])

with col2:
    st.subheader("🏦 Extratos Bancários")
    st.caption("Arraste os extratos de múltiplos bancos de uma só vez.")
    arq_bancos = st.file_uploader("Extratos (.csv)", type=['csv'], accept_multiple_files=True)

st.divider()

# --- 4. MOTOR E DASHBOARD ---
if st.button("🚀 Processar Auditoria e Gerar Insights", use_container_width=True):
    
    if not arq_sistema or not arq_bancos:
        st.warning("⚠️ Ação bloqueada: É obrigatório enviar o arquivo do ERP e pelo menos um Extrato Bancário para iniciar o motor.")
    else:
        with st.spinner("Analisando integridade dos dados e cruzando bases..."):
            try: # TRATAMENTO DE ERROS GENÉRICOS (O sistema não quebra na tela do cliente)
                
                # Leitura Inicial
                df_sistema = pd.read_csv(arq_sistema, sep=';')
                
                # Validação de Schema do ERP
                schema_erp = ['Cliente', 'Valor_Esperado']
                if not validar_schema(df_sistema, schema_erp, "ERP"):
                    st.stop() # Para a execução se o arquivo estiver errado
                
                # Leitura e Empilhamento dos Bancos
                lista_dfs_bancos = []
                schema_banco = ['Descricao_Banco', 'Valor_Recebido', 'Banco']
                
                for arquivo in arq_bancos:
                    df_temp = pd.read_csv(arquivo, sep=';')
                    if not validar_schema(df_temp, schema_banco, arquivo.name):
                        st.stop() # Para se qualquer banco vier com coluna errada
                    lista_dfs_bancos.append(df_temp)
                    
                df_banco_consolidado = pd.concat(lista_dfs_bancos, ignore_index=True)
                
                # Limpeza e Padronização
                lixo_bancario = ['TED ', 'PIX ', 'DOC ', ' - DUPLICADO']
                df_banco_consolidado['Cliente_Extraido'] = df_banco_consolidado['Descricao_Banco']
                for lixo in lixo_bancario:
                    df_banco_consolidado['Cliente_Extraido'] = df_banco_consolidado['Cliente_Extraido'].str.replace(lixo, '')
                
                df_sistema['Cliente'] = df_sistema['Cliente'].str.strip().str.upper()
                
                # Cruzamento (LEFT JOIN)
                df_cruzamento = pd.merge(df_sistema, df_banco_consolidado, left_on='Cliente', right_on='Cliente_Extraido', how='left', validate='1:m')
                
                # Regras Contábeis
                df_cruzamento['Valor_Recebido'] = df_cruzamento['Valor_Recebido'].fillna(0)
                df_cruzamento['Banco'] = df_cruzamento['Banco'].fillna('Não Localizado')
                df_cruzamento['Diferenca_R$'] = df_cruzamento['Valor_Esperado'] - df_cruzamento['Valor_Recebido']
                
                # Status
                condicoes = [
                    (df_cruzamento['Diferenca_R$'] == 0),
                    (df_cruzamento['Diferenca_R$'] > 0),
                    (df_cruzamento['Diferenca_R$'] < 0)
                ]
                status = ['Conciliado (OK)', 'Pendente / Parcial', 'Duplicado / A Maior']
                df_cruzamento['Status'] = np.select(condicoes, status, default='Erro')
                
                resultado_visual = df_cruzamento[['Cliente', 'Banco', 'Valor_Esperado', 'Valor_Recebido', 'Diferenca_R$', 'Status']]
                df_excecoes = resultado_visual[resultado_visual['Status'] != 'Conciliado (OK)']

                # --- 5. DASHBOARD DE INSIGHTS (A Mágica) ---
                st.success("✅ Processamento concluído com sucesso!")
                
                st.markdown("### 📊 Visão Executiva")
                
                # Cartões de Métricas
                total_esperado = df_cruzamento['Valor_Esperado'].sum()
                total_recebido = df_cruzamento['Valor_Recebido'].sum()
                total_pendente = df_cruzamento.loc[df_cruzamento['Diferenca_R$'] > 0, 'Diferenca_R$'].sum()
                
                metrica1, metrica2, metrica3 = st.columns(3)
                metrica1.metric("Valor Total Esperado", f"R$ {total_esperado:,.2f}")
                metrica2.metric("Valor Total Conciliado", f"R$ {total_recebido:,.2f}")
                metrica3.metric("Risco / Inadimplência", f"R$ {total_pendente:,.2f}", delta="- Atenção", delta_color="inverse")
                
                st.divider()
                
                # Gráficos com Plotly
                graf_col1, graf_col2 = st.columns(2)
                
                with graf_col1:
                    st.markdown("#### Distribuição de Status")
                    fig_pizza = px.pie(df_cruzamento, names='Status', hole=0.4, color='Status',
                                       color_discrete_map={'Conciliado (OK)':'#2e7d32', 'Pendente / Parcial':'#d32f2f', 'Duplicado / A Maior':'#fbc02d'})
                    st.plotly_chart(fig_pizza, use_container_width=True)
                    
                with graf_col2:
                    st.markdown("#### Top 5 Maiores Pendências (R$)")
                    df_top5 = df_cruzamento[df_cruzamento['Diferenca_R$'] > 0].nlargest(5, 'Diferenca_R$')
                    if not df_top5.empty:
                        fig_barra = px.bar(df_top5, x='Cliente', y='Diferenca_R$', text_auto='.2s', color='Diferenca_R$', color_continuous_scale='Reds')
                        st.plotly_chart(fig_barra, use_container_width=True)
                    else:
                        st.info("Nenhuma pendência encontrada.")

                st.divider()

                # Tabela e Download
                st.markdown("### 📋 Relatório Detalhado de Exceções para Auditoria")
                st.dataframe(df_excecoes, use_container_width=True)
                
                st.download_button(
                    label="📥 Baixar Relatório Completo (.CSV)",
                    data=df_excecoes.to_csv(index=False, sep=';').encode('utf-8'),
                    file_name='relatorio_auditoria.csv',
                    mime='text/csv'
                )

            except Exception as e:
                st.error(f"❌ Ocorreu um erro crítico ao processar os arquivos. Certifique-se de que são CSVs válidos separados por ponto e vírgula (;). Erro técnico: {e}")