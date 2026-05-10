import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

# --- إعدادات الواجهة الاحترافية ---
st.set_page_config(
    page_title="بورصة الوحيد", 
    page_icon="logo.png", # تأكد من وجود ملف logo.png في GitHub
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS مخصص لتحويله لشكل App احترافي (إخفاء بعض عناصر streamlit)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #000033; color: white; } /* خلفية كحلي احترافية */
    div.stButton > button { background-color: #006400; color: white; border-radius: 5px; }
    .css-1n76uvr { background-color: #00008B; } /* Sidebar */
    </style>
    """, unsafe_allow_html=True)

# --- محرك التحليل الذكي ---
def get_advanced_analysis(symbol):
    df = yf.download(symbol, period="6mo", interval="1d", progress=False)
    if df.empty: return None
    
    # حساب المتوسطات
    df['MA21'] = ta.sma(df['Close'], length=21)
    df['MA50'] = ta.sma(df['Close'], length=50)
    df['MA100'] = ta.sma(df['Close'], length=100)
    df['MA200'] = ta.sma(df['Close'], length=200)

    # خوارزمية تحديد القاع والقمة (Trend Change Detection)
    # نبحث عن أقل قاع (Swing Low) وأعلى قمة (Swing High) في آخر 120 يوم
    recent_data = df.tail(120)
    low_idx = recent_data['Low'].idxmin()
    # نبحث عن القمة التي تكونت *بعد* هذا القاع فقط
    after_low = recent_data.loc[low_idx:]
    if len(after_low) > 1:
        high_idx = after_low['High'].idxmax()
    else:
        high_idx = recent_data['High'].idxmax()

    low_p = float(df.loc[low_idx, 'Low'])
    high_p = float(df.loc[high_idx, 'High'])
    
    diff = high_p - low_p
    fib_levels = {
        "100% (Base)": low_p,
        "78.6%": low_p + 0.214 * diff,
        "61.8% (Golden)": low_p + 0.382 * diff,
        "50.0%": low_p + 0.5 * diff,
        "38.2%": low_p + 0.618 * diff,
        "23.6%": low_p + 0.764 * diff,
        "0% (Top)": high_p
    }
    
    return df, fib_levels, low_p, high_p, low_idx, high_idx

# --- واجهة التطبيق ---
st.image("logo.png", width=150) # لوجو بورصة الوحيد
st.markdown("<h1 style='text-align: center; color: #00FF00;'>منصة الوحيد للتحليل الفني</h1>", unsafe_allow_html=True)

symbol_input = st.text_input("🔍 ادخل رمز السهم (مثال: COMI.CA, FWRY.CA, TMGH.CA)", value="COMI.CA").upper()

if symbol_input:
    with st.spinner('جاري قراءة الشارت وتحديد مناطق الانعكاس...'):
        df, fibs, l_p, h_p, l_idx, h_idx = get_advanced_analysis(symbol_input)
        last_price = df['Close'].iloc[-1]

        # عرض المتوسطات
        cols = st.columns(4)
        ma_list = [21, 50, 100, 200]
        for i, ma in enumerate(ma_list):
            ma_val = df[f'MA{ma}'].iloc[-1]
            status = "✅ فوق" if last_price > ma_val else "❌ تحت"
            cols[i].metric(f"MA {ma}", f"{ma_val:.2f}", delta=status, delta_color="normal")

        # عرض فيبوناتشي
        st.markdown(f"### 🎯 تحليل فيبوناتشي من قاع {l_p:.2f} إلى قمة {h_p:.2f}")
        
        # الرسم البياني
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="السعر"))
        
        # رسم خطوط الفيبو
        colors = ['gray', 'red', 'gold', 'orange', 'blue', 'purple', 'green']
        for (lvl, val), color in zip(fibs.items(), colors):
            fig.add_hline(y=val, line_dash="dash", line_color=color, annotation_text=lvl)

        fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # قسم التقارير المالية (روابط مباشرة)
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📑 التقارير المالية")
            st.link_button("فتح التقارير في مباشر", f"https://www.mubasher.info/markets/EGX/stocks/{symbol_input.split('.')[0]}/financial-statements")
        with c2:
            st.subheader("📰 آخر الأخبار")
            st.link_button("أخبار البورصة المصرية", "https://www.egx.com.eg/ar/news.aspx")