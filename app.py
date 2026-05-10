import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# محاولة استدعاء مكتبة التحليل الفني بأمان لتجنب توقف التطبيق
try:
    import pandas_ta as ta
except Exception:
    pass

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="بورصة الوحيد Pro", layout="wide", initial_sidebar_state="expanded")

# تصميم CSS احترافي مستوحى من N-CURE
st.markdown("""
    <style>
        :root { --primary: #1a6b3c; --bg: #0e1117; --card-bg: #161b22; }
        .stApp { background-color: var(--bg); color: white; }
        .main-header {
            background: linear-gradient(90deg, #1a6b3c, #2d3436);
            padding: 20px; text-align: center; border-radius: 15px;
            margin-bottom: 25px; border-bottom: 4px solid #f1c40f;
        }
        .metric-card {
            background: var(--card-bg); padding: 15px; border-radius: 12px;
            border-right: 5px solid var(--primary); margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .status-up { color: #00ff88; font-weight: bold; }
        .status-down { color: #ff4d4d; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. وظيفة Pushbullet ---
def send_push(title, body):
    TOKEN = "o.IsheoB5YdMDPr63vCJGxAkQ6PuoyKiam"
    try:
        res = requests.post('https://api.pushbullet.com/v2/pushes', 
                            auth=(TOKEN, ''), 
                            json={"type": "note", "title": title, "body": body})
        return res.status_code == 200
    except:
        return False

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("### 🔍 التحكم والبحث")
    symbol_input = st.text_input("رمز السهم (مثلاً: COMI, FWRY)", "COMI").upper()
    ticker = f"{symbol_input}.CA"
    
    st.divider()
    st.markdown("### 🔔 التنبيهات")
    target_price = st.number_input("نبهني عند سعر:", value=0.0)
    if st.button("تفعيل التنبيه"):
        if target_price > 0:
            if send_push("بورصة الوحيد", f"تم تفعيل مراقبة {symbol_input} عند {target_price}"):
                st.success("تم الربط بالموبايل ✅")

# --- 4. واجهة التطبيق الرئيسية ---
st.markdown(f'<div class="main-header"><h1>💎 منصة الوحيد للتحليل المباشر - {symbol_input}</h1></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 التحليل الفني", "📰 الأخبار", "🎯 الماسح الذكي", "💧 السيولة"])

# جلب البيانات
@st.cache_data(ttl=3600)
def get_data(t):
    return yf.download(t, period="2y", interval="1d", progress=False)

df = get_data(ticker)

with tab1:
    if not df.empty:
        col_chart, col_stats = st.columns([3, 1])
        with col_chart:
            # شارت ترادينج فيو المباشر
            tv_html = f"""
            <div style="height:550px;">
                <div id="tv_chart" style="height:100%;"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                    "autosize": true, "symbol": "EGX:{symbol_input}", "interval": "D",
                    "timezone": "Africa/Cairo", "theme": "dark", "style": "1",
                    "locale": "ar", "container_id": "tv_chart"
                }});
                </script>
            </div>"""
            components.html(tv_html, height=560)
            
        with col_stats:
            last_price = float(df['Close'].iloc[-1])
            st.markdown(f'<div class="metric-card"><h3>السعر</h3><h2>{last_price:.2f}</h2></div>', unsafe_allow_html=True)
            
            # حساب المتوسطات
            for ma_val in [21, 50, 100, 200]:
                ma = df['Close'].rolling(ma_val).mean().iloc[-1]
                status = "✅ فوق" if last_price > ma else "❌ تحت"
                color = "status-up" if last_price > ma else "status-down"
                st.markdown(f"MA {ma_val}: <span class='{color}'>{status}</span>", unsafe_allow_html=True)

with tab2:
    st.info("🔗 مصادر الأخبار الرسمية")
    st.markdown(f"- [أخبار {symbol_input} على مباشر](https://www.mubasher.info/markets/EGX/stocks/{symbol_input})")
    st.markdown("- [إفصاحات البورصة المصرية](https://www.egx.com.eg/ar/news.aspx)")

with tab4:
    st.markdown("### 💧 سجل السيولة (آخر 5 أيام)")
    st.table(df[['Close', 'Volume']].tail(5))
