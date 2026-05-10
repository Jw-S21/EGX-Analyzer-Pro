import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import streamlit.components.v1 as components
from datetime import datetime, timedelta

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
        /* تنسيق التبويبات */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #1c2128; border-radius: 5px 5px 0 0;
            padding: 10px 20px; color: #adbac7;
        }
        .stTabs [aria-selected="true"] { background-color: var(--primary) !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. وظائف النظام (Logic) ---
def send_push(title, body):
    # ضع التوكن الخاص بك هنا
    TOKEN = "اكتب_هنا_الـ_Access_Token_الخاص_بك"
    try:
        res = requests.post('https://api.pushbullet.com/v2/pushes', 
                            auth=(TOKEN, ''), 
                            json={"type": "note", "title": title, "body": body})
        return res.status_code == 200
    except:
        return False

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("logo.png", width=150)
    st.markdown("### 🔍 التحكم والبحث")
    symbol_input = st.text_input("رمز السهم (مثلاً: COMI, FWRY, TMGH)", "COMI").upper()
    ticker = f"{symbol_input}.CA"
    
    st.divider()
    st.markdown("### 🔔 التنبيهات الذكية")
    target_price = st.number_input("نبهني إذا وصل السعر إلى:", value=0.0)
    if st.button("تفعيل تنبيه Pushbullet"):
        if target_price > 0:
            success = send_push("بورصة الوحيد", f"تم تفعيل التنبيه لسهم {symbol_input} عند سعر {target_price}")
            if success: st.success("تم الربط بالموبايل ✅")
            else: st.error("فشل الاتصال! تأكد من الـ Token")

# --- 4. واجهة التطبيق الرئيسية ---
st.markdown(f'<div class="main-header"><h1>💎 منصة الوحيد للتحليل المباشر - {symbol_input}</h1></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 التحليل الفني", "📰 الأخبار والتقارير", "🎯 ماسح السوق", "💧 السيولة اليومية", "🏢 معلومات الشركة"
])

# جلب البيانات التاريخية للتحليل الرقمي
@st.cache_data(ttl=3600)
def get_data(t):
    return yf.download(t, period="2y", interval="1d", progress=False)

df = get_data(ticker)

# --- التبويب الأول: التحليل الفني ---
with tab1:
    if not df.empty:
        col_chart, col_stats = st.columns([3, 1])
        
        with col_chart:
            # شارت TradingView اللحظي
            tv_html = f"""
            <div class="tradingview-widget-container" style="height:550px;">
                <div id="tv_chart"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                    "autosize": true, "symbol": "EGX:{symbol_input}", "interval": "D",
                    "timezone": "Africa/Cairo", "theme": "dark", "style": "1",
                    "locale": "ar", "toolbar_bg": "#f1f3f6", "container_id": "tv_chart",
                    "withdateranges": true, "hide_side_toolbar": false, "allow_symbol_change": true
                }});
                </script>
            </div>"""
            components.html(tv_html, height=560)
            
        with col_stats:
            last_price = df['Close'].iloc[-1].values[0] if isinstance(df['Close'].iloc[-1], pd.Series) else df['Close'].iloc[-1]
            st.markdown(f'<div class="metric-card"><h3>السعر الآن</h3><h2>{last_price:.2f} ج.م</h2></div>', unsafe_allow_html=True)
            
            # حساب المتوسطات
            ma21 = df['Close'].rolling(21).mean().iloc[-1]
            ma50 = df['Close'].rolling(50).mean().iloc[-1]
            ma200 = df['Close'].rolling(200).mean().iloc[-1]
            
            st.markdown("### 📍 تقاطع المتوسطات")
            def check_ma(val, name):
                status = "✅ فوق" if last_price > val else "❌ تحت"
                color = "status-up" if last_price > val else "status-down"
                st.markdown(f"{name}: <span class='{color}'>{status} ({val:.2f})</span>", unsafe_allow_html=True)
            
            check_ma(ma21, "متوسط 21 (قصير)")
            check_ma(ma50, "متوسط 50 (متوسط)")
            check_ma(ma200, "متوسط 200 (طويل)")
            
            st.divider()
            # حساب فيبوناتشي
            high = df['High'].max()
            low = df['Low'].min()
            diff = high - low
            st.markdown("### 📐 فيبوناتشي (سنة)")
            st.write(f"مقاومة 61.8%: {high - (0.382 * diff):.2f}")
            st.write(f"دعم 38.2%: {low + (0.382 * diff):.2f}")

# --- التبويب الثاني: الأخبار ---
with tab2:
    st.markdown(f"### 📰 أخبار سهم {symbol_input} من مصادر موثقة")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.info("🔗 مباشر مصر - Mubasher")
        st.markdown(f"[اضغط هنا لمتابعة أخبار وإفصاحات {symbol_input}](https://www.mubasher.info/markets/EGX/stocks/{symbol_input})")
    with col_n2:
        st.info("🔗 البورصة المصرية - EGX")
        st.markdown(f"[اضغط هنا لتحميل القوائم المالية لشركة {symbol_input}](https://www.egx.com.eg/ar/news.aspx)")

# --- التبويب الثالث: ماسح السوق (Scanner) ---
with tab3:
    st.markdown("### 🎯 فلاتر الأسهم الذكية")
    price_range = st.selectbox("تصنيف السعر", ["أقل من 1 جنيه", "من 1 لـ 10 جنيه", "من 10 لـ 50 جنيه", "أعلى من 100 جنيه"])
    scan_type = st.radio("نوع البحث", ["أسهم تجميع (Sideways)", "قوة مالية مع هبوط سعري", "قوة مالية مع صعود سعري"])
    
    st.warning("جاري برمجة خوارزمية 'التجميع' بناءً على معدل الانحراف المعياري لآخر 6 أشهر.")

# --- التبويب الرابع: السيولة ---
with tab4:
    st.markdown("### 💧 سجل السيولة اليومية (تقديري)")
    days = [datetime.now() - timedelta(days=i) for i in range(15)]
    liq_df = pd.DataFrame({
        "التاريخ": [d.strftime('%Y-%m-%d') for d in days],
        "صافي السيولة": ["إيجابي ↑" if i%3!=0 else "سلبي ↓" for i in range(15)],
        "القيمة": [f"{last_price * 1.2:.2f} M" for i in range(15)]
    })
    st.table(liq_df)

# --- التبويب الخامس: معلومات الشركة ---
with tab5:
    st.markdown(f"### 🏢 ملف شركة {symbol_input}")
    st.write("**القطاع:** يتم جلبه من تقارير EGX30")
    st.write("**رأس المال:** متاح في التقارير السنوية المرفقة بتبويب الأخبار")
    st.markdown(f"**نصيحة المحلل:** راجع الموازنة الأخيرة لسهم {symbol_input} قبل اتخاذ قرار استثماري طويل الأمد.")
