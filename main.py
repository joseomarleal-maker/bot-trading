import os
import yfinance as yf
import pandas as pd
import requests
from flask import Flask

app = Flask(__name__)

# Lee las credenciales de forma segura desde Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def enviar_mensaje(mensaje):
    if TELEGRAM_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mensaje}
        try:
            requests.post(url, json=payload)
            print("Mensaje enviado a Telegram correctamente.")
        except Exception as e:
            print(f"Error enviando a Telegram: {e}")
    else:
        print("Faltan las variables TELEGRAM_TOKEN o CHAT_ID en Render.")

@app.route('/')
def home():
    try:
        df = yf.download("BTC-USD", period="1d", interval="15m")
        if not df.empty:
            df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            ultimo_close = float(df['Close'].iloc[-1])
            ultima_ema9 = float(df['EMA_9'].iloc[-1])
            ultima_ema21 = float(df['EMA_21'].iloc[-1])
            
            # Formatear el mensaje de alerta
            status = f"🤖 ¡Bot Activo!\n📈 BTC-USD: ${ultimo_close:.2f}\n📊 EMA9: {ultima_ema9:.2f} | EMA21: {ultima_ema21:.2f}"
            
            # ENVIAR MENSAJE EN VIVO A TELEGRAM
            enviar_mensaje(status)
            
            return status
        return "Bot corriendo, pero sin datos de mercado."
    except Exception as e:
        return f"Error en el bot: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
