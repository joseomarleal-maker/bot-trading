import os
import time
import requests
import warnings
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime
from threading import Thread
from flask import Flask

warnings.filterwarnings("ignore")

# 🌐 CONFIGURACIÓN DEL MINI SERVIDOR WEB PARA RENDER
app = Flask('')

@app.route('/')
def home():
    return "¡Bot de Trading Activo 24/7 en la Nube!"

def run_web_server():
    # Render asigna automáticamente un puerto, usamos 8080 por defecto
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 🔴 TUS CREDENCIALES DE TELEGRAM VERIFICADAS
TOKEN_TELEGRAM = "8451771652:AAGaRcMMipizwj1zj95oZCzu51-Zn1J1To4"
ID_CHAT = "6600690280"
MERCADOS = ["EURUSD=X", "EURGBP=X", "EURJPY=X", "EURCHF=X", "EURCAD=X", "EURAUD=X", "EURNZD=X"]

def enviar_alerta_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": ID_CHAT, "text": mensaje}
    try: requests.post(url, json=payload)
    except Exception as e: print(f"Error Telegram: {e}")

# 📊 BUCLE PRINCIPAL DE TRADING (IGUAL AL TUYO)
def bot_trading_loop():
    print("🛡️ Iniciando escaneo constante en la nube...")
    while True:
        hora_actual = datetime.now().strftime('%H:%M:%S')
        for activo in MERCADOS:
            try:
                nombre_bonito = activo.replace("=X", "").replace("USD", "/USD").replace("GBP", "/GBP").replace("JPY", "/JPY").replace("CHF", "/CHF").replace("CAD", "/CAD").replace("AUD", "/AUD").replace("NZD", "/NZD")
                
                datos = yf.download(activo, period="2d", interval="1m", progress=False)
                if datos.empty or len(datos) < 50: continue
                    
                if isinstance(datos.columns, pd.MultiIndex):
                    datos.columns = datos.columns.droplevel(1)
                datos.columns = datos.columns.str.lower()
                
                datos['ema_50'] = ta.ema(datos['close'], length=50)
                datos['rsi'] = ta.rsi(datos['close'], length=14)
                
                bbands = ta.bbands(datos['close'], length=20, std=2)
                datos['bb_lower'] = bbands['BBL_20_2.0']
                datos['bb_upper'] = bbands['BBU_20_2.0']
                
                ultima_vela = datos.iloc[-1]
                precio = ultima_vela['close']
                rsi = ultima_vela['rsi']
                ema = ultima_vela['ema_50']
                bb_inf = ultima_vela['bb_lower']
                bb_sup = ultima_vela['bb_upper']
                
                if precio > ema and rsi <= 30 and precio <= bb_inf:
                    msg = f"🚨 ALERTA NUBE: COMPRA (SUBE) 🟢\n\n🎯 Divisa: {nombre_bonito}\nPrecio: {precio:.5f}\n⚡ RSI: {rsi:.2f}\n\n🎯 Operación a 1-2 min en IQ Option."
                    enviar_alerta_telegram(msg)
                    time.sleep(10)
                    
                elif precio < ema and rsi >= 70 and precio >= bb_sup:
                    msg = f"🚨 ALERTA NUBE: VENTA (BAJA) 🔴\n\n🎯 Divisa: {nombre_bonito}\nPrecio: {precio:.5f}\n⚡ RSI: {rsi:.2f}\n\n🎯 Operación a 1-2 min en IQ Option."
                    enviar_alerta_telegram(msg)
                    time.sleep(10)
                    
            except Exception:
                pass
        time.sleep(15)

if __name__ == "__main__":
    # Arrancar el servidor web en un hilo secundario y el bot en el principal
    t = Thread(target=run_web_server)
    t.start()
    bot_trading_loop()
