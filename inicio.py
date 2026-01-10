import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="B3 VIP", layout="centered")

st.markdown("""
    <style>
    /* Esconder elementos nativos */
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* Ajuste de espaçamento do topo */
    .block-container {
        padding-top: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN (CORRIGIDO)
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 ÁREA DO ASSINANTE B3 VIP")
    # Removido o erro de sintaxe da linha abaixo
    senha = st.text_input("Chave de Acesso:", type="password")
    if st.button("Liberar"):
        if senha == "mestre10":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. APP PRINCIPAL
st.title("📈 ANÁLISE DE SETUP B3 VIP")
ticker = st.text_input("Ativo (Ex: PETR4, VALE3):", "PETR4")

if st.button("Consultar"):
    try:
        nome_ativo = ticker.upper().strip()
        simbolo = f"{nome_ativo}.SA" if not nome_ativo.endswith(".SA") else nome_ativo
        
        # Download dos dados
        df = yf.download(simbolo, period="120d", interval="1d", progress=False)
        
        if df.empty:
            st.error("Ativo não encontrado.")
        else:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # --- LÓGICA DE STOPS ---
            p_loss, p_gain = (3.0, 5.0) if any(x in nome_ativo for x in ["BOVA", "IVVB", "SMAL"]) else \
                             (4.0, 6.0) if nome_ativo.endswith("34") else (5.0, 8.0)

            # --- INDICADORES ---
            df['EMA69'] = df.ta.ema(length=69)
            stoch = df.ta.stoch(k=14, d=3)
            dmi = df.ta.adx(length=14)
            df = pd.concat([df, stoch, dmi], axis=1)
            
            # --- LÓGICA DE ENTRADA ---
            c1 = df['Close'] > df['EMA69']
            c2 = df['DMP_14'] > df['DMN_14']
            c3 = df['STOCHk_14_3_3'] < 80
            c4 = df['Close'] > df['High'].shift(1)
            
            df['Sinal'] = c1 & c2 & c3 & c4
            sinal_hoje = bool(df['Sinal'].iloc[-1])
            atual = float(df['Close'].iloc[-1])
            
            st.metric(f"Preço Atual {nome_ativo}", f"R$ {atual:.2f}")
            st.write("---")

            st.subheader("🔍 Checklist do Setup")
            st.write(f"{'✅' if c1.iloc[-1] else '❌'} Indic 1")
            st.write(f"{'✅' if c2.iloc[-1] else '❌'} Indic 2")
            st.write(f"{'✅' if c3.iloc[-1] else '❌'} Indic 3")
            st.write(f"{'✅' if c4.iloc[-1] else '❌'} Indic 4")
            
            st.write("---")

            if sinal_hoje:
                # Localizar data e preço da primeira entrada deste ciclo
                idx_entrada = len(df) - 1
                for i in range(len(df)-1, 0, -1):
                    if df['Sinal'].iloc[i]:
                        idx_entrada = i
                    else:
                        break
                
                dt_entrada = df.index[idx_entrada].strftime('%d/%m/%Y')
                pr_entrada = float(df['Close'].iloc[idx_entrada])
                
                st.success(f"🚀 COMPRA LIBERADA!")
                st.write(f"**Data da Entrada:** {dt_entrada}")
                st.write(f"**Preço na Entrada:** R$ {pr_entrada:.2f}")
                
                variacao = ((atual / pr_entrada) - 1) * 100
                if variacao > 0.5:
                    st.warning(f"⚠️ Já subiu {variacao:.2f}% desde a entrada.")
                elif variacao < -0.5:
                    st.info(f"📉 Está {abs(variacao):.2f}% abaixo da entrada.")
            else:
                st.error("🚫 COMPRA NÃO LIBERADA")

            # --- PLANEJAMENTO ---
            st.subheader("🎯 Planejamento")
            st.write(f"**🛑 Stop Loss:** R$ {atual * (1-(p_loss/100)):.2f} ({p_loss}%)")
            st.write(f"**💰 Alvo Gain:** R$ {atual * (1+(p_gain/100)):.2f} ({p_gain}%)")
            st.write(f"**📊 Risco/Retorno:** {(p_gain/p_loss):.1f}")
            
            st.write("---")
            
            # --- GRÁFICO ---
            st.subheader("📊 Gráfico + Média")
            # Preparando os dados para o gráfico com legendas claras
            df_plot = df[['Close', 'EMA69']].copy()
            df_plot.columns = ['Preço de Fechamento', 'Média EMA 69']
            st.line_chart(df_plot)
            
    except Exception as e:
        st.error(f"Erro ao processar ativo. Verifique o ticker.")

st.info("Para sair, feche o navegador.")
