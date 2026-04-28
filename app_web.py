import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuração da Página
st.set_page_config(page_title="Motor de Reconciliação", page_icon="📊", layout="wide")

st.title("📊 Portal de Auditoria e Reconciliação Contábil")
st.markdown("Faça o upload do relatório do sistema e de **quantos extratos bancários quiser**.")

st.divider()

# 2. Criando o Layout Inteligente (2 Colunas)
col1, col2 = st.columns(2)

with col1:
    st.subheader("🖥️ Sistema ERP (TOTVS/SAP)")
    arq_sistema = st.file_uploader("Arquivo do Sistema (.csv)", type=['csv'])

with col2:
    st.subheader("🏦 Extratos Bancários")
    
    # Injetando HTML para colocar as logos reais dos bancos (Itaú, Bradesco, Santander, BB)
    st.markdown("""
        <div style="display: flex; gap: 15px; margin-bottom: 10px;">
            <img src="https://logodownload.org/wp-content/uploads/2014/05/itau-logo-1.png" width="35" style="border-radius: 5px;">
            <img src="https://logodownload.org/wp-content/uploads/2018/09/bradesco-logo-1.png" width="35" style="border-radius: 5px;">
            <img src="https://logodownload.org/wp-content/uploads/2014/05/santander-logo-1.png" width="35" style="border-radius: 5px;">
            <img src="https://logodownload.org/wp-content/uploads/2014/05/banco-do-brasil-logo-1.png" width="35" style="border-radius: 5px;">
        </div>
    """, unsafe_allow_html=True)
    
    # O segredo: accept_multiple_files=True permite arrastar dezenas de arquivos de uma vez!
    arq_bancos = st.file_uploader("Arraste TODOS os extratos aqui (.csv)", type=['csv'], accept_multiple_files=True)

st.divider()

# 3. O Botão de Ação
if st.button("🚀 Processar Auditoria", use_container_width=True):
    
    # Verifica se há o sistema e pelo menos UM banco anexado (arq_bancos agora é uma lista)
    if arq_sistema and arq_bancos:
        
        with st.spinner("O Motor está cruzando os dados..."):
            
            # --- LÓGICA DINÂMICA ---
            df_sistema = pd.read_csv(arq_sistema, sep=';')
            df_sistema['Cliente'] = df_sistema['Cliente'].str.strip().str.upper()
            
            # Aqui está a inteligência: um loop para ler quantos arquivos de banco o usuário colocou
            lista_dfs_bancos = []
            for arquivo in arq_bancos:
                df_temp = pd.read_csv(arquivo, sep=';')
                lista_dfs_bancos.append(df_temp)
                
            # Junta todos os bancos que estavam na lista
            df_banco_consolidado = pd.concat(lista_dfs_bancos, ignore_index=True)
            
            # Limpeza
            lixo_bancario = ['TED ', 'PIX ', 'DOC ', ' - DUPLICADO']
            df_banco_consolidado['Cliente_Extraido'] = df_banco_consolidado['Descricao_Banco']
            for lixo in lixo_bancario:
                df_banco_consolidado['Cliente_Extraido'] = df_banco_consolidado['Cliente_Extraido'].str.replace(lixo, '')
            
            # Cruzamento
            df_cruzamento = pd.merge(df_sistema, df_banco_consolidado, left_on='Cliente', right_on='Cliente_Extraido', how='left', validate='1:m')
            
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
            
            # --- EXIBIÇÃO ---
            st.success(f"✅ Auditoria finalizada! Lemos {len(arq_bancos)} extratos bancários de uma vez. Encontramos {len(df_excecoes)} divergências.")
            st.dataframe(resultado_visual, use_container_width=True)
            
            st.download_button(
                label="📥 Baixar Relatório de Exceções",
                data=df_excecoes.to_csv(index=False, sep=';').encode('utf-8'),
                file_name='relatorio_auditoria.csv',
                mime='text/csv'
            )
            
    else:
        st.warning("⚠️ Por favor, anexe o arquivo do sistema e pelo menos um extrato bancário.")