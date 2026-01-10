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
ticker = st.text_input("Ativo (Ex: CURY3, BOVA11, AAPL34):", "CURY3")

if st.button("Consultar"):
    try:
        nome_ativo = ticker.upper().strip()
        simbolo_busca = f"{nome_ativo}.SA" if not nome_ativo.endswith(".SA") else nome_ativo
            
        df = yf.download(simbolo_busca, period="150d", interval="1d")
        
        if df.empty:
            st.error("Ativo não encontrado.")
        else:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # --- LÓGICA DE IDENTIFICAÇÃO DO TIPO DE ATIVO (SEU MANUAL) ---
            if any(etf in nome_ativo for etf in ["BOVA11", "IVVB11", "SMAL11", "DIVO11", "HAS11"]):
                tipo = "ETF"
                perc_loss, perc_gain = 3.0, 5.0
            elif nome_ativo.endswith("34") or nome_ativo.endswith("35"):
                tipo = "BDR"
                perc_loss, perc_gain = 4.0, 6.0
            else:
                tipo = "Ação"
                perc_loss, perc_gain = 5.0, 8.0

            # --- CÁLCULO DOS INDICADORES ---
            df['EMA 69'] = ta.ema(df['Close'], length=69)
            stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
            df = pd.concat([df, stoch], axis=1)
            dmi = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            df = pd.concat([df, dmi], axis=1)
            
            preco_atual = float(df['Close'].iloc[-1])
            v_ema69 = float(df['EMA 69'].iloc[-1])
            v_stoch_k = float(df['STOCHk_14_3_3'].iloc[-1])
            v_di_plus = float(df['DMP_14'].iloc[-1])
            v_di_minus = float(df['DMN_14'].iloc[-1])
            maxima_anterior = float(df['High'].iloc[-2])
            
            st.metric(f"Preço Atual ({nome_ativo})", f"R$ {preco_atual:.2f}")
            st.write("---")

            # --- CHECKLIST TÉCNICO ---
            st.subheader("🔍 Checklist do Setup")
            c1 = preco_atual > v_ema69
            c2 = v_di_plus > v_di_minus
            c3 = v_stoch_k < 80 
            c4 = preco_atual > maxima_anterior
            
            st.write(f"{'✅' if c1 else '❌'} Preço acima da EMA 69")
            st.write(f"{'✅' if c2 else '❌'} DMI: DI+ acima do DI-")
            st.write(f"{'✅' if c3 else '❌'} Estocástico Favorável")
            st.write(f"{'✅' if c4 else '❌'} Rompimento da Máxima Anterior")
            
            st.write("---")

            if all([c1, c2, c4]):
                st.success(f"🚀 COMPRA LIBERADA PARA {tipo}!")
            else:
                st.error("🚫 COMPRA NÃO LIBERADA")

            st.write("---")
            
            # --- STOPS ---
            stop_loss = preco_atual * (1 - (perc_loss/100))
            stop_gain = preco_atual * (1 + (perc_gain/100))
            risco_retorno = perc_gain / perc_loss

            st.subheader("🎯 Planejamento da Operação")
            st.write(f"**🛑 Stop Loss ({perc_loss}%):** R$ {stop_loss:.2f}")
            st.write(f"**💰 Alvo Gain ({perc_gain}%):** R$ {stop_gain:.2f}")
            st.write(f"**📊 Risco/Retorno:** {risco_retorno:.1f} {'✅' if risco_retorno >= 1.5 else '⚠️'}")
            
            st.write("---")
            
            # --- GRÁFICO COM LEGENDA ---
            st.subheader(f"📊 Gráfico: {nome_ativo} + EMA 69")
            
            # Criamos um dataframe apenas com o que queremos no gráfico para a legenda aparecer
            df_grafico = df[['Close', 'EMA 69']].copy()
            df_grafico.columns = [nome_ativo, 'EMA 69'] # Renomeia colunas para a legenda
            
            st.line_chart(df_grafico)
            
    except Exception as e:
        st.error(f"Erro ao processar: {e}")

st.info("Para sair, basta fechar o navegador.")
