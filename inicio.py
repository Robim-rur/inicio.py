import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. Configuração Visual e BLOQUEIO TOTAL de Menus
st.set_page_config(page_title="B3 VIP - SETUP", layout="centered")

st.markdown("""
    <style>
    /* Bloqueio de menus e ícones do sistema */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden !important;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stSidebarNav"] {display: none;}
    .stAppDeployButton {display: none !important;}
    .block-container {padding-top: 1rem;}
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

# 3. App de Análise
st.title("📈 Análise de Setup B3")
ticker = st.text_input("Ativo (Ex: CURY3, BOVA11):", "PETR4")

if st.button("Consultar"):
    try:
        nome_ativo = ticker.upper().strip()
        simbolo = f"{nome_ativo}.SA" if not nome_ativo.endswith(".SA") else nome_ativo
            
        df = yf.download(simbolo, period="100d", interval="1d", progress=False)
        
        if df.empty:
            st.error("Ativo não encontrado.")
        else:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # --- LÓGICA DE STOPS ---
            if any(x in nome_ativo for x in ["BOVA11", "IVVB11", "SMAL11"]):
                tipo, p_loss, p_gain = "ETF", 3.0, 5.0
            elif nome_ativo.endswith("34"):
                tipo, p_loss, p_gain = "BDR", 4.0, 6.0
            else:
                tipo, p_loss, p_gain = "Ação", 5.0, 8.0

            # --- INDICADORES (OCULTOS NO NOME) ---
            df['EMA69'] = df.ta.ema(length=69)
            stoch = df.ta.stoch(k=14, d=3)
            dmi = df.ta.adx(length=14)
            
            atual = float(df['Close'].iloc[-1])
            m69 = float(df['EMA69'].iloc[-1])
            sk = float(stoch['STOCHk_14_3_3'].iloc[-1])
            dp = float(dmi['DMP_14'].iloc[-1])
            dm = float(dmi['DMN_14'].iloc[-1])
            max_ant = float(df['High'].iloc[-2])
            
            st.metric(f"{nome_ativo} ({tipo})", f"R$ {atual:.2f}")
            st.write("---")

            # --- CHECKLIST DISCRETO ---
            st.subheader("🔍 Checklist do Setup")
            
            c1 = atual > m69
            c2 = dp > dm
            c3 = sk < 80 
            c4 = atual > max_ant
            
            # Substituição dos nomes por Indic 1, 2, 3 e 4
            st.write(f"{'✅' if c1 else '❌'} Indic 1")
            st.write(f"{'✅' if c2 else '❌'} Indic 2")
            st.write(f"{'✅' if c3 else '❌'} Indic 3")
            st.write(f"{'✅' if c4 else '❌'} Indic 4")
            
            st.write("---")

            if all([c1, c2, c4]):
                st.success("🚀 COMPRA LIBERADA!")
            else:
                st.error("🚫 COMPRA NÃO LIBERADA")

            # --- PLANEJAMENTO ---
            loss = atual * (1 - (p_loss/100))
            gain = atual * (1 + (p_gain/100))
            rr = p_gain / p_loss

            st.subheader("🎯 Planejamento")
            st.write(f"**🛑 Stop Loss ({p_loss}%):** R$ {loss:.2f}")
            st.write(f"**💰 Alvo Gain ({p_gain}%):** R$ {gain:.2f}")
            st.write(f"**📊 Risco/Retorno:** {rr:.1f} {'✅' if rr >= 1.5 else '⚠️'}")
            
            st.write("---")
            
            # --- GRÁFICO ---
            st.subheader("📊 Gráfico Histórico + Média")
            grafico_data = pd.DataFrame({
                f"Preço {nome_ativo}": df['Close'],
                "Média": df['EMA69']
            })
            st.line_chart(grafico_data)
            
    except Exception as e:
        st.error("Erro ao carregar dados.")

st.info("Para sair, feche o navegador.")
