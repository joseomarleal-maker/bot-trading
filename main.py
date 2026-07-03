import os
import yfinance as yf
import pandas as pd
import requests
from flask import Flask

app = Flask(__name__)

# Configura tu token y chat_id de Telegram aquí
TELEGRAM_TOKEN = "TU_TELEGRAM_TOKEN_AQUÍ"
CHAT_ID = "TU_CHAT_ID_AQUÍ"

def enviar_mensaje(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

@app.route('/')
def home():
    try:
        # Analizar ejemplo con Bitcoin (puedes cambiar el símbolo si gustas)
        df = yf.download("BTC-USD", period="1d", interval="15m")
        if not df.empty:
            # Calcular medias móviles simples directo con Pandas
            df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            ultimo_close = float(df['Close'].iloc[-1])
            ultima_ema9 = float(df['EMA_9'].iloc[-1])
            ultima_ema21 = float(df['EMA_21'].iloc[-1])
            
            status = f"Bot Activo. BTC-USD: ${ultimo_close:.2f} | EMA9: {ultima_ema9:.2f} | EMA21: {ultima_ema21:.2f}"
            print(status)
            return status
        return "Bot corriendo, pero no se recibieron datos de mercado."
    except Exception as e:
        return f"Error en el bot: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
