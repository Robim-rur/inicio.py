import streamlit as st
import yfinance as yf

st.set_page_config(page_title="B3 VIP", layout="centered")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login B3 VIP")
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha == "mestre10":
            st.session_state.auth = True
            st.rerun()
    st.stop()

st.title("📈 Monitor B3")
ticker = st.text_input("Ativo (Ex: PETR4):", "PETR4")
if st.button("Consultar"):
    try:
        df = yf.download(f"{ticker}.SA", period="1mo")
        st.metric("Preço Atual", f"R$ {df['Close'].iloc[-1]:.2f}")
        st.line_chart(df['Close'])
    except:
        st.error("Erro ao buscar dados.")
