import streamlit as st
import yfinance as yf
import pandas as pd

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
            
        # Busca dados históricos
        df = yf.download(nome_ativo, period="60d", interval="1d")
        
        if df.empty:
            st.error("Ativo não encontrado.")
        else:
            # Limpeza de colunas do Yahoo Finance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Dados atuais
            preco_atual = float(df['Close'].iloc[-1])
            maxima_hoje = float(df['High'].iloc[-1])
            minima_hoje = float(df['Low'].iloc[-1])
            fechamento_anterior = float(df['Close'].iloc[-2])
            
            # Lógica do Setup (Baseada na máxima anterior)
            maxima_anterior = float(df['High'].iloc[-2])
            data_entrada = df.index[-1].strftime('%d/%m/%Y')
            
            st.metric("Preço Atual", f"R$ {preco_atual:.2f}")
            st.write("---")

            # --- ANÁLISE TÉCNICA DO SETUP ---
            st.subheader("🔍 Análise Técnica")
            
            if preco_atual > maxima_anterior:
                st.success(f"✅ **SINAL DE COMPRA ATIVADO**")
                st.write(f"O preço rompeu a máxima anterior de R$ {maxima_anterior:.2f}.")
                st.write(f"**Data do Sinal:** {data_entrada}")
            else:
                st.warning(f"⏳ **AGUARDANDO ROMPIMENTO**")
                st.write(f"O ativo precisa superar R$ {maxima_anterior:.2f} para liberar compra.")

            # Análise de Tendência Curta
            if preco_atual > fechamento_anterior:
                st.info("📈 **Tendência:** Alta no curto prazo (Preço acima do fechamento anterior).")
            else:
                st.error("📉 **Tendência:** Baixa no curto prazo (Preço abaixo do fechamento anterior).")

            st.write("---")
            
            # --- STOPS E PORCENTAGENS ---
            perc_loss = 3.0  
            perc_gain = 6.0  
            stop_loss = preco_atual * (1 - (perc_loss/100))
            stop_gain = preco_atual * (1 + (perc_gain/100))

            st.write(f"**🛑 Stop Loss ({perc_loss}%):** R$ {stop_loss:.2f}")
            st.write(f"**💰 Alvo Gain ({perc_gain}%):** R$ {stop_gain:.2f}")
            
            st.write("---")
            
            # --- GRÁFICO E DADOS TÉCNICOS ---
            st.subheader("📊 Gráfico Histórico")
            st.line_chart(df['Close'])
            
            st.write(f"**Resumo Técnico:** Máxima: R$ {maxima_hoje:.2f} | Mínima: R$ {minima_hoje:.2f}")
            
            st.success("Análise processada com sucesso!")
            
    except Exception as e:
        st.error(f"Erro ao processar setup: {e}")

st.info("Para sair, basta fechar o navegador.")
