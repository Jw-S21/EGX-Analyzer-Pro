import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import streamlit.components.v1 as components

# --- 1. إعدادات الهوية البصرية ---
st.set_page_config(page_title="بورصة الوحيد Pro", layout="wide")

st.markdown("""
    <style>
        :root { --primary: #1a6b3c; --bg: #0e1117; }
        .stApp { background-color: var(--bg); color: white; }
        .main-header { background: linear-gradient(90deg, #1a6b3c, #2d3436); padding: 20px; text-align: center; border-radius: 15px; margin-bottom: 25px; border-bottom: 4px solid #f1c40f; }
        .metric-card { background: #161b22; padding: 15px; border-radius: 12px; border-right: 5px solid #1a6b3c; margin-bottom: 15px; }
        .status-up { color: #00ff88; font-weight: bold; }
        .status-down { color: #ff4d4d; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. نظام التنبيهات (Pushbullet) ---
def send_push(title, body):
    TOKEN = "o.IsheoB5YdMDPr63vCJGxAkQ6PuoyKiam"
    try:
        requests.post('https://api.pushbullet.com/v2/pushes', auth=(TOKEN, ''), json={"type": "note", "title": title, "body": body})
        return True
    except: return False

# --- 3. القائمة الجانبية ---
with st.sidebar:
    st.markdown("### 🔍 البحث والتحكم")
    symbol_input = st.text_input("رمز السهم", "COMI").upper()
    ticker = f"{symbol_input}.CA"
    target_price = st.number_input("سعر التنبيه للموبايل", value=0.0)
    if st.button("تفعيل التنبيه ✅"):
        if send_push("بورصة الوحيد", f"بدأت مراقبة {symbol_input}"):
            st.success("تم الربط بموبايلك!")

# --- 4. الواجهة الرئيسية والبيانات ---
st.markdown(f'<div class="main-header"><h1>💎 منصة الوحيد للتحليل الفني - {symbol_input}</h1></div>', unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_full_data(t):
    return yf.download(t, period="2y", interval="1d", progress=False)

df = get_full_data(ticker)

tab1, tab2, tab3 = st.tabs(["📊 التحليل الرقمي", "📰 الأخبار", "💧 السيولة اليومية"])

if not df.empty:
    # تنظيف البيانات لضمان دقة الحسابات
    df_close = df['Close'].copy()
    last_price = float(df_close.iloc[-1])

    with tab1:
        col_chart, col_stats = st.columns([3, 1])
        with col_chart:
            # شارت ترادينج فيو المباشر
            tv_html = f'<div style="height:550px;"><div id="tv_chart" style="height:100%;"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{"autosize": true, "symbol": "EGX:{symbol_input}", "interval": "D", "timezone": "Africa/Cairo", "theme": "dark", "style": "1", "locale": "ar", "container_id": "tv_chart", "withdateranges": true, "hide_side_toolbar": false}});</script></div>'
            components.html(tv_html, height=560)

        with col_stats:
            st.markdown(f'<div class="metric-card"><h3>السعر الآن</h3><h2>{last_price:.2f} ج.م</h2></div>', unsafe_allow_html=True)
            
            # --- تحليل المتوسطات ---
            st.markdown("### 📍 المتوسطات")
            for m in [21, 50, 100, 200]:
                ma_val = float(df_close.rolling(window=m).mean().iloc[-1])
                status = "✅ فوق" if last_price > ma_val else "❌ تحت"
                color = "status-up" if last_price > ma_val else "status-down"
                st.markdown(f"**MA {m}:** <span class='{color}'>{status} ({ma_val:.2f})</span>", unsafe_allow_html=True)

            st.divider()
            # --- تحليل فيبوناتشي (سنة) ---
            st.markdown("### 📐 فيبوناتشي (سنوي)")
            high = float(df['High'].max())
            low = float(df['Low'].min())
            diff = high - low
            st.write(f"مقاومة 61.8%: **{high - (0.382 * diff):.2f}**")
            st.write(f"نقطة 50%: **{high - (0.500 * diff):.2f}**")
            st.write(f"دعم 38.2%: **{low + (0.382 * diff):.2f}**")

    with tab2:
        st.markdown(f"### [🔗 اضغط هنا لمتابعة أخبار وإفصاحات {symbol_input} على مباشر مصر](https://www.mubasher.info/markets/EGX/stocks/{symbol_input})")

    with tab3:
        st.markdown("### 💧 حجم التداول والسيولة (آخر 10 أيام)")
        # عرض الفوليوم اليومي
        vol_df = df[['Close', 'Volume']].tail(10).copy()
        vol_df.columns = ['سعر الإغلاق', 'حجم التداول (Volume)']
        st.dataframe(vol_df.sort_index(ascending=False), use_container_width=True)
else:
    st.error("لم نتمكن من جلب بيانات هذا السهم، تأكد من الرمز.")
