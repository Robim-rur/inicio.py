import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. CONFIGURAÇÃO DA PÁGINA (WIDE - Ideal para incorporar em sites)
st.set_page_config(
    page_title="B3 VIP", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# CSS para limpeza visual
st.markdown("""
    <style>
    /* Esconde menus e botões de gerenciamento */
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* Ajuste de margem para o topo */
    .block-container {
        padding-top: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE LOGIN
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 ÁREA DO ASSINANTE B3 VIP")
    senha = st.text_input("Chave de Acesso:", type="password")
    if st.button("Liberar"):
        if senha == "mestre10":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. APLICATIVO PRINCIPAL
st.title("📈 ANÁLISE DE SETUP B3 VIP")
ticker = st.text_input("Digite o Ativo (Ex: PETR4, VALE3, BOVA11):", "PETR4")

if st.button("Consultar Ativo"):
    try:
        nome_ativo = ticker.upper().strip()
        simbolo = f"{nome_ativo}.SA" if not nome_ativo.endswith(".SA") else nome_ativo
        
        # Download dos dados (120 dias para garantir o cálculo da EMA69)
        df = yf.download(simbolo, period="120d", interval="1d", progress=False)
        
        if df.empty:
            st.error("Ativo não encontrado. Verifique se o código está correto.")
        else:
            # Tratamento de colunas MultiIndex do Yahoo Finance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # --- DEFINIÇÃO DE STOP E ALVO POR TIPO DE ATIVO ---
            if any(x in nome_ativo for x in ["BOVA", "IVVB", "SMAL"]):
                p_loss, p_gain = 3.0, 5.0
            elif nome_ativo.endswith("34"):
                p_loss, p_gain = 4.0, 6.0
            else:
                p_loss, p_gain = 5.0, 8.0

            # --- CÁLCULO DOS INDICADORES TÉCNICOS ---
            df['EMA69'] = df.ta.ema(length=69)
            stoch = df.ta.stoch(k=14, d=3)
            dmi = df.ta.adx(length=14)
            df = pd.concat([df, stoch, dmi], axis=1)
            
            # --- REGRAS DO SETUP ---
            cond_1 = df['Close'] > df['EMA69']
            cond_2 = df['DMP_14'] > df['DMN_14']
            cond_3 = df['STOCHk_14_3_3'] < 80
            cond_4 = df['Close'] > df['High'].shift(1)
            
            df['Sinal'] = cond_1 & cond_2 & cond_3 & cond_4
            sinal_hoje = bool(df['Sinal'].iloc[-1])
            preco_atual = float(df['Close'].iloc[-1])
            
            # Exibição do Preço
            st.metric(f"Preço Atual {nome_ativo}", f"R$ {preco_atual:.2f}")
            st.write("---")

            # Checklist Visual
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🔍 Checklist")
                st.write(f"{'✅' if cond_1.iloc[-1] else '❌'} Preço > Média 69")
                st.write(f"{'✅' if cond_2.iloc[-1] else '❌'} DMI+ > DMI-")
                st.write(f"{'✅' if cond_3.iloc[-1] else '❌'} Estocástico < 80")
                st.write(f"{'✅' if cond_4.iloc[-1] else '❌'} Superou Máxima Anterior")

            # Lógica de Entrada (Data e Preço)
            if sinal_hoje:
                idx_entrada = len(df) - 1
                for i in range(len(df)-1, 0, -1):
                    if df['Sinal'].iloc[i]:
                        idx_entrada = i
                    else:
                        break
                
                dt_entrada = df.index[idx_entrada].strftime('%d/%m/%Y')
                pr_entrada = float(df['Close'].iloc[idx_entrada])
                
                with col2:
                    st.success("🚀 COMPRA LIBERADA!")
                    st.write(f"**Data da Entrada:** {dt_entrada}")
                    st.write(f"**Preço na Entrada:** R$ {pr_entrada:.2f}")
                    
                    variacao = ((preco_atual / pr_entrada) - 1) * 100
                    if variacao > 0.5:
                        st.warning(f"⚠️ Já subiu {variacao:.2f}% desde a entrada.")
                    elif variacao < -0.5:
                        st.info(f"📉 Está {abs(variacao):.2f}% abaixo da entrada.")
            else:
                with col2:
                    st.error("🚫 COMPRA NÃO LIBERADA")

            st.write("---")

            # --- PLANEJAMENTO DE TRADE ---
            st.subheader("🎯 Planejamento de Risco")
            val_loss = preco_atual * (1 - (p_loss/100))
            val_gain = preco_atual * (1 + (p_gain/100))
            
            c_loss, c_gain, c_rr = st.columns(3)
            c_loss.metric("Stop Loss", f"R$ {val_loss:.2f}", f"-{p_loss}%", delta_color="inverse")
            c_gain.metric("Alvo Gain", f"R$ {val_gain:.2f}", f"+{p_gain}%")
            c_rr.metric("Risco/Retorno", f"1 : {(p_gain/p_loss):.1f}")
            
            st.write("---")
            
            # --- GRÁFICO ---
            st.subheader("📊 Gráfico com Média EMA 69")
            df_plot = df[['Close', 'EMA69']].copy()
            df_plot.columns = ['Preço de Fechamento', 'Média EMA 69']
            st.line_chart(df_plot)
            
    except Exception as e:
        st.error("Erro ao processar dados. Tente novamente em instantes.")

st.markdown("---")
st.caption("B3 VIP - Sistema de Análise Técnica")
