import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuração da Página
st.set_page_config(page_title="Motor de Reconciliação", page_icon="📊", layout="wide")

st.title("📊 Portal de Auditoria e Reconciliação Contábil")
st.markdown("Faça o upload dos extratos bancários e do relatório do sistema para gerar a auditoria automática.")

st.divider() # Linha visual para separar as seções

# 2. Criando as caixas de Upload (Arraste e Solte)
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🖥️ Sistema ERP")
    arq_sistema = st.file_uploader("Arquivo do Sistema (.csv)", type=['csv'])

with col2:
    st.subheader("🏦 Banco Itaú")
    arq_itau = st.file_uploader("Extrato Itaú (.csv)", type=['csv'])

with col3:
    st.subheader("🏦 Banco Bradesco")
    arq_bradesco = st.file_uploader("Extrato Bradesco (.csv)", type=['csv'])

st.divider()

# 3. O Botão de Ação
if st.button("🚀 Processar Auditoria", use_container_width=True):
    
    # Verifica se o usuário anexou os 3 arquivos antes de rodar
    if arq_sistema and arq_itau and arq_bradesco:
        
        with st.spinner("O Motor está cruzando os dados..."):
            
            # --- LÓGICA DO BACKEND EMBUTIDA ---
            # O Streamlit lê o arquivo que o usuário arrastou para a tela
            df_sistema = pd.read_csv(arq_sistema, sep=';')
            df_itau = pd.read_csv(arq_itau, sep=';')
            df_bradesco = pd.read_csv(arq_bradesco, sep=';')
            
            # Empilhando Bancos
            df_banco_consolidado = pd.concat([df_itau, df_bradesco], ignore_index=True)
            
            # Limpeza
            lixo_bancario = ['TED ', 'PIX ', 'DOC ', ' - DUPLICADO']
            df_banco_consolidado['Cliente_Extraido'] = df_banco_consolidado['Descricao_Banco']
            for lixo in lixo_bancario:
                df_banco_consolidado['Cliente_Extraido'] = df_banco_consolidado['Cliente_Extraido'].str.replace(lixo, '')
            
            df_sistema['Cliente'] = df_sistema['Cliente'].str.strip().str.upper()
            
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
            
            # Filtro de Exceções
            df_excecoes = resultado_visual[resultado_visual['Status'] != 'Conciliado (OK)']
            
            # --- EXIBIÇÃO NO FRONTEND ---
            st.success(f"✅ Auditoria finalizada! Encontramos {len(df_excecoes)} divergências que precisam de atenção.")
            
            # Mostra a tabela lindamente na tela do navegador
            st.dataframe(resultado_visual, use_container_width=True)
            
            # Botão para o usuário baixar o relatório pronto
            st.download_button(
                label="📥 Baixar Relatório de Exceções",
                data=df_excecoes.to_csv(index=False, sep=';').encode('utf-8'),
                file_name='relatorio_auditoria.csv',
                mime='text/csv'
            )
            
    else:
        st.warning("⚠️ Por favor, faça o upload dos 3 arquivos para liberar o motor.")