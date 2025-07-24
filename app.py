import streamlit as st
from deriv_bot import DerivBot

st.set_page_config(page_title="Robô Deriv - Over 7", layout="centered")
st.title("🤖 Robô Deriv - Estratégia Over 7 com Martingale")

api_token = st.text_input("🔑 Token da API da Deriv", type="password")
stake = st.number_input("💰 Valor de Entrada Inicial", min_value=0.35, value=1.0, step=0.5)
martingale_factor = st.number_input("📈 Fator de Martingale", min_value=1.0, value=2.0, step=0.1)
max_losses = st.number_input("❌ Limite de Perdas Consecutivas", min_value=1, value=3)
profit_target = st.number_input("🎯 Meta de Lucro (USD)", min_value=1.0, value=10.0)
stop_loss = st.number_input("🛑 Stop Loss (USD)", min_value=1.0, value=10.0)

run_bot = st.button("🚀 Iniciar Robô")

if run_bot and api_token:
    bot = DerivBot(api_token, stake, martingale_factor, max_losses, profit_target, stop_loss)
    bot.run()