import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. Configuração Visual
st.set_page_config(page_title="B3 VIP - SETUP", layout="centered")

st.markdown("""
    <style>
    header, footer, .stDeployButton {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

# 2. Sistema de Login
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Área do Assinante B3")
    senha = st.text_input("Chave de Acesso:", type="password")
    if st.button("Liberar"):
        if senha == "mestre10":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. App de Análise de Setup
st.title("📈 Análise de Setup B3")
ticker = st.text_input("Ativo (Ex: PETR4):", "PETR4")

if st.button("Consultar"):
    try:
        nome_ativo = ticker.upper().strip()
        if not nome_ativo.endswith(".SA"):
            nome_ativo = f"{nome_ativo}.SA"
            
        # Busca dados (150 dias para a EMA 69)
        df = yf.download(nome_ativo, period="150d", interval="1d")
        
        if df.empty:
            st.error("Ativo não encontrado.")
        else:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # --- CÁLCULO DOS INDICADORES ---
            df['EMA69'] = ta.ema(df['Close'], length=69)
            stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
            df = pd.concat([df, stoch], axis=1)
            dmi = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            df = pd.concat([df, dmi], axis=1)
            
            preco_atual = float(df['Close'].iloc[-1])
            v_ema69 = float(df['EMA69'].iloc[-1])
            v_stoch_k = float(df['STOCHk_14_3_3'].iloc[-1])
            v_di_plus = float(df['DMP_14'].iloc[-1])
            v_di_minus = float(df['DMN_14'].iloc[-1])
            maxima_anterior = float(df['High'].iloc[-2])
            
            st.metric("Preço Atual", f"R$ {preco_atual:.2f}")
            st.write("---")

            # --- CHECKLIST TÉCNICO ---
            st.subheader("🔍 Checklist do Setup")
            
            c1 = preco_atual > v_ema69
            c2 = v_di_plus > v_di_minus
            c3 = v_stoch_k < 80 
            c4 = preco_atual > maxima_anterior
            
            st.write(f"{'✅' if c1 else '❌'} Preço acima da EMA 69 (R$ {v_ema69:.2f})")
            st.write(f"{'✅' if c2 else '❌'} DI+ ({v_di_plus:.1f}) acima do DI- ({v_di_minus:.1f})")
            st.write(f"{'✅' if c3 else '❌'} Estocástico Favorável ({v_stoch_k:.1f})")
            st.write(f"{'✅' if c4 else '❌'} Rompimento da Máxima Anterior (R$ {maxima_anterior:.2f})")
            
            st.write("---")

            if all([c1, c2, c4]):
                st.success("🚀 COMPRA LIBERADA!")
                st.write(f"**Data da Entrada:** {df.index[-1].strftime('%d/%m/%Y')}")
            else:
                st.error("🚫 COMPRA NÃO LIBERADA")

            st.write("---")
            
            # --- STOPS ---
            perc_loss = 3.0  
            perc_gain = 6.0  
            stop_loss = preco_atual * (1 - (perc_loss/100))
            stop_gain = preco_atual * (1 + (perc_gain/100))

            st.write(f"**🛑 Stop Loss ({perc_loss}%):** R$ {stop_loss:.2f}")
            st.write(f"**💰 Alvo Gain ({perc_gain}%):** R$ {stop_gain:.2f}")
            
            st.write("---")
            st.subheader("📊 Gráfico Histórico")
            st.line_chart(df['Close'])
            
    except Exception as e:
        st.error(f"Erro ao processar setup: {e}")

st.info("Para sair, basta fechar o navegador.")
