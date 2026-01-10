import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuração da Página e Estilo (Igual ao anterior)
st.set_page_config(page_title="B3 VIP", layout="centered")

st.markdown("""
    <style>
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
    st.title("🔐 Login B3 VIP")
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha == "mestre10":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. Conteúdo Principal
st.title("📈 Monitor B3")
ticker = st.text_input("Ativo (Ex: PETR4):", "PETR4")

if st.button("Consultar"):
    try:
        nome_ativo = ticker.upper().strip()
        if not nome_ativo.endswith(".SA"):
            nome_ativo = f"{nome_ativo}.SA"
            
        with st.spinner('Buscando...'):
            df = yf.download(nome_ativo, period="1mo")
            
        if df.empty:
            st.error("Ativo não encontrado.")
        else:
            # Extração dos dados técnicos
            preco_atual = float(df['Close'].iloc[-1])
            maxima = float(df['High'].iloc[-1])
            minima = float(df['Low'].iloc[-1])
            abertura = float(df['Open'].iloc[-1])
            
            # Cálculos de Stop (Padrão 3%)
            stop_loss = preco_atual * 0.97
            stop_gain = preco_atual * 1.06

            # Exibição Simples e Direta
            st.metric("Preço Atual", f"R$ {preco_atual:.2f}")
            
            st.write("---")
            st.write(f"**Dados Técnicos do Dia ({ticker}):**")
            st.write(f"🔺 Máxima: R$ {maxima:.2f}")
            st.write(f"🔻 Mínima: R$ {minima:.2f}")
            st.write(f"🏁 Abertura: R$ {abertura:.2f}")
            
            st.write("---")
            st.write("**Sugestão de Stops:**")
            st.write(f"🛑 Stop Loss: R$ {stop_loss:.2f}")
            st.write(f"🎯 Stop Gain: R$ {stop_gain:.2f}")

            st.write("---")
            st.subheader("Variação no Último Mês")
            # Força o gráfico a usar os dados de fechamento
            st.line_chart(df['Close'])
            
            st.success("Dados atualizados com sucesso!")
            
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")

st.info("Para sair, basta fechar o navegador.")
