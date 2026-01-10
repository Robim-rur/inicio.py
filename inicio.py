import streamlit as st
import yfinance as yf

# 1. Configuração da Página e Remoção de Menus/Barras
st.set_page_config(page_title="B3 VIP", layout="centered")

st.markdown("""
    <style>
    /* Esconde o menu superior, o rodapé e o botão de Deploy do Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# 2. Sistema de Login
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acesso Restrito - B3 VIP")
    senha = st.text_input("Digite sua chave de acesso:", type="password")
    if st.button("Liberar Sistema"):
        if senha == "mestre10":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()

# 3. Conteúdo Principal (Só aparece após o login)
st.title("📈 Monitor de Ativos B3")
ticker = st.text_input("Digite o código da ação (ex: PETR4, VALE3):", "PETR4")

if st.button("Consultar Agora"):
    try:
        # Garante que o código tenha o .SA no final para o Yahoo Finance
        nome_ativo = ticker.upper().strip()
        if not nome_ativo.endswith(".SA"):
            nome_ativo = f"{nome_ativo}.SA"
            
        with st.spinner('Buscando dados na Bolsa...'):
            # Busca os dados
            df = yf.download(nome_ativo, period="1mo")
            
        if df.empty:
            st.warning(f"Não encontramos dados para '{nome_ativo}'. Verifique o código digitado.")
        else:
            # Correção do erro técnico: Extraímos o valor real do número antes de formatar
            preco_fechamento = df['Close'].iloc[-1]
            
            # Converte para número real (float) para evitar erro de formato da Series
            valor_final = float(preco_fechamento)
            
            st.metric(label=f"Preço Atual de {nome_ativo}", value=f"R$ {valor_final:.2f}")
            
            st.subheader("Variação no Último Mês")
            st.line_chart(df['Close'])
            
            st.success("Dados atualizados com sucesso!")
            
    except Exception as e:
        st.error(f"Ocorreu um erro técnico: {e}")

st.info("Para sair, basta fechar o navegador.")
