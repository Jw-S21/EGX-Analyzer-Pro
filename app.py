import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import streamlit.components.v1 as components

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="بورصة الوحيد Pro", layout="wide")

st.markdown("""
    <style>
        :root { --primary: #1a6b3c; --bg: #0e1117; }
        .stApp { background-color: var(--bg); color: white; }
        .main-header { background: #1a6b3c; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px; }
        .metric-card { background: #161b22; padding: 15px; border-radius: 10px; border-right: 5px solid #1a6b3c; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. التنبيهات ---
def send_push(title, body):
    TOKEN = "o.IsheoB5YdMDPr63vCJGxAkQ6PuoyKiam"
    try:
        requests.post('https://api.pushbullet.com/v2/pushes', auth=(TOKEN, ''), json={"type": "note", "title": title, "body": body})
        return True
    except: return False

# --- 3. القائمة الجانبية ---
with st.sidebar:
    symbol_input = st.text_input("رمز السهم", "COMI").upper()
    ticker = f"{symbol_input}.CA"
    target_price = st.number_input("سعر التنبيه", value=0.0)
    if st.button("تفعيل التنبيه"):
        if send_push("بورصة الوحيد", f"تم تفعيل مراقبة {symbol_input}"):
            st.success("تم الربط ✅")

# --- 4. الواجهة الرئيسية ---
st.markdown(f'<div class="main-header"><h1>💎 منصة الوحيد - {symbol_input}</h1></div>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📊 التحليل الفني", "📰 الأخبار"])

@st.cache_data(ttl=3600)
def get_data(t):
    return yf.download(t, period="2y", interval="1d", progress=False)

df = get_data(ticker)

with tab1:
    if not df.empty:
        col_chart, col_stats = st.columns([3, 1])
        with col_chart:
            # شارت ترادينج فيو المباشر
            tv_html = f'<div style="height:500px;"><div id="tv_chart" style="height:100%;"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{"autosize": true, "symbol": "EGX:{symbol_input}", "interval": "D", "timezone": "Africa/Cairo", "theme": "dark", "style": "1", "locale": "ar", "container_id": "tv_chart"}});</script></div>'
            components.html(tv_html, height=520)
            
        with col_stats:
            # حساب المتوسطات يدوياً بدون مكتبات خارجية
            last_price = float(df['Close'].iloc[-1])
            st.markdown(f'<div class="metric-card"><h3>السعر</h3><h2>{last_price:.2f}</h2></div>', unsafe_allow_html=True)
            
            for m in [21, 50, 100, 200]:
                ma_val = df['Close'].rolling(window=m).mean().iloc[-1]
                st.write(f"MA {m}: {'✅ فوق' if last_price > ma_val else '❌ تحت'} ({ma_val:.2f})")

with tab2:
    st.markdown(f"[أخبار {symbol_input} على مباشر](https://www.mubasher.info/markets/EGX/stocks/{symbol_input})")
