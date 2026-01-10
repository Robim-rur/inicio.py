import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. CONFIGURAÇÃO E BLINDAGEM TOTAL (CSS BRUTAMONTES)
st.set_page_config(page_title="B3 VIP", layout="centered")

st.markdown("""
    <style>
    /* 1. Esconde o botão 'Manage app' e 'Deploy' mesmo para o dono */
    .stAppDeployButton, .stDeployButton, [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* 2. Esconde o menu de 3 linhas e o cabeçalho */
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}

    /* 3. Remove o espaço branco no topo que sobrava */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -50px !important;
    }
    
    /* 4. Desativa qualquer clique acidental no topo */
    header {pointer-events: none !important;}
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN
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

# 3. APP PRINCIPAL
st.title("📈 ANÁLISE DE SETUP B3 VIP")
ticker = st.text_input("Ativo (Ex: PETR4, VALE3):", "PETR4")

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
                p_loss, p_gain = 3.0, 5.0
            elif nome_ativo.endswith("34"):
                p_loss, p_gain = 4.0, 6.0
            else:
                p_loss, p_gain = 5.0, 8.0

            # --- INDICADORES ---
            df['EMA69'] = df.ta.ema(length=69)
            stoch = df.ta.stoch(k=14, d=3)
            dmi = df.ta.adx(length=14)
            df = pd.concat([df, stoch, dmi], axis=1)
            
            # --- LÓGICA DE ENTRADA ---
            cond_1 = df['Close'] > df['EMA69']
            cond_2 = df['DMP_14'] > df['DMN_14']
            cond_3 = df['STOCHk_14_3_3'] < 80
            cond_4 = df['Close'] > df['High'].shift(1)
            
            df['Sinal'] = cond_1 & cond_2 & cond_3 & cond_4
            sinal_hoje = bool(df['Sinal'].iloc[-1])
            atual = float(df['Close'].iloc[-1])
            
            st.metric(f"Preço Atual {nome_ativo}", f"R$ {atual:.2f}")
            st.write("---")

            st.subheader("🔍 Checklist do Setup")
            st.write(f"{'✅' if cond_1.iloc[-1] else '❌'} Indic 1")
            st.write(f"{'✅' if cond_2.iloc[-1] else '❌'} Indic 2")
            st.write(f"{'✅' if cond_3.iloc[-1] else '❌'} Indic 3")
            st.write(f"{'✅' if cond_4.iloc[-1] else '❌'} Indic 4")
            
            st.write("---")

            if sinal_hoje:
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
            loss = atual * (1 - (p_loss/100))
            gain = atual * (1 + (p_gain/100))
            rr = p_gain / p_loss

            st.subheader("🎯 Planejamento")
            st.write(f"**🛑 Stop Loss:** R$ {loss:.2f} ({p_loss}%)")
            st.write(f"**💰 Alvo Gain:** R$ {gain:.2f} ({p_gain}%)")
            st.write(f"**📊 Risco/Retorno:** {rr:.1f}")
            
            st.write("---")
            
            st.subheader("📊 Gráfico + Média")
            chart_data = pd.DataFrame({
                "Preço": df['Close'],
                "Média": df['EMA69']
            })
            st.line_chart(chart_data)
            
    except Exception as e:
        st.error("Erro técnico.")

st.info("Para sair, feche o navegador.")
