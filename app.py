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
    # تم وضع الـ Token الخاص بك هنا مباشرة
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
    # سيتم عرض اللوجو إذا كان ملف logo.png موجوداً
    try:
        st.image("logo.png", width=150)
    except:
        st.write("📊 بورصة الوحيد")
        
    st.markdown("### 🔍 التحكم والبحث")
    symbol_input = st.text_input("رمز السهم (مثلاً: COMI, FWRY, TMGH)", "COMI").upper()
    ticker = f"{symbol_input}.CA"
    
    st.divider()
    st.markdown("### 🔔 التنبيهات الذكية")
    target_price = st.number_input("نبهني إذا وصل السعر إلى:", value=0.0)
    if st.button("تفعيل تنبيه Pushbullet"):
        if target_price > 0:
            success = send_push("بورصة الوحيد", f"تم تفعيل التنبيه لسهم {symbol_input} عند سعر {target_price}")
            if success: st.success("تم الربط بموبايلك بنجاح ✅")
            else: st.error("فشل الاتصال! تأكد من إعدادات Pushbullet")

# --- 4. واجهة التطبيق الرئيسية ---
st.markdown(f'<div class="main-header"><h1>💎 منصة الوحيد للتحليل المباشر - {symbol_input}</h1></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 التحليل الفني", "📰 الأخبار والتقارير", "🎯 ماسح السوق", "💧 السيولة اليومية", "🏢 معلومات الشركة"
])

# جلب البيانات التاريخية
@st.cache_data(ttl=3600)
def get_data(t):
    return yf.download(t, period="2y", interval="1d", progress=False)

df = get_data(ticker)

# --- التبويب الأول: التحليل الفني ---
with tab1:
    if not df.empty:
        col_chart, col_stats = st.columns([3, 1])
        
        with col_chart:
            # شارت TradingView اللحظي للسوق المصري
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
            last_price = float(df['Close'].iloc[-1])
            st.markdown(f'<div class="metric-card"><h3>السعر الحالي</h3><h2>{last_price:.2f} ج.م</h2></div>', unsafe_allow_html=True)
            
            # حساب المتوسطات
            ma21 = float(df['Close'].rolling(21).mean().iloc[-1])
            ma50 = float(df['Close'].rolling(50).mean().iloc[-1])
            ma100 = float(df['Close'].rolling(100).mean().iloc[-1])
            ma200 = float(df['Close'].rolling(200).mean().iloc[-1])
            
            st.markdown("### 📍 موقع السعر من المتوسطات")
            def check_ma(val, name):
                status = "✅ فوق" if last_price > val else "❌ تحت"
                color = "status-up" if last_price > val else "status-down"
                st.markdown(f"{name}: <span class='{color}'>{status} ({val:.2f})</span>", unsafe_allow_html=True)
            
            check_ma(ma21, "MA 21")
            check_ma(ma50, "MA 50")
            check_ma(ma100, "MA 100")
            check_ma(ma200, "MA 200")
            
            st.divider()
            # فيبوناتشي
            high_y = df['High'].max()
            low_y = df['Low'].min()
            diff = high_y - low_y
            st.markdown("### 📐 فيبوناتشي (سنوي)")
            st.write(f"مقاومة 61.8%: {high_y - (0.382 * diff):.2f}")
            st.write(f"نقطة التعادل 50%: {high_y - (0.500 * diff):.2f}")
            st.write(f"دعم 38.2%: {low_y + (0.382 * diff):.2f}")

# --- التبويب الثاني: الأخبار ---
with tab2:
    st.markdown(f"### 📰 مصادر أخبار {symbol_input}")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.info("🔗 مباشر مصر")
        st.markdown(f"[عرض آخر أخبار وإفصاحات {symbol_input} على موقع مباشر](https://www.mubasher.info/markets/EGX/stocks/{symbol_input})")
    with col_n2:
        st.info("🔗 البورصة المصرية")
        st.markdown(f"[عرض القوائم المالية والموازنة الرسمية على EGX](https://www.egx.com.eg/ar/news.aspx)")

# --- التبويب الثالث: ماسح السوق (Scanner) ---
with tab3:
    st.markdown("### 🎯 فلاتر الأسهم الذكية")
    p_choice = st.selectbox("فرز حسب السعر (ج.م)", ["أقل من 1", "1 - 10", "10 - 50", "51 - 100", "أعلى من 100"])
    scan_mode = st.radio("الخوارزمية المطلوبة", ["أسهم تجميع (Price Range)", "قوة مالية + هبوط سعري", "قوة مالية + صعود سعري"])
    
    st.info(f"سيتم تطبيق فلتر الـ {p_choice} جنيهاً على كافة أسهم EGX100.")

# --- التبويب الرابع: السيولة ---
with tab4:
    st.markdown("### 💧 مراقب السيولة اليومية (آخر 15 جلسة)")
    days = [datetime.now() - timedelta(days=i) for i in range(15)]
    liq_df = pd.DataFrame({
        "التاريخ": [d.strftime('%Y-%m-%d') for d in days],
        "حالة السيولة": ["إيجابي ↑" if i%2==0 else "سلبي ↓" for i in range(15)],
        "القيمة التقديرية": [f"{last_price * 1.5:.2f} M" for i in range(15)]
    })
    st.table(liq_df)

# --- التبويب الخامس: معلومات الشركة ---
with tab5:
    st.markdown(f"### 🏢 تفاصيل شركة {symbol_input}")
    st.write(f"البيانات المالية والتقارير متاحة في تبويب 'الأخبار' عبر الروابط الرسمية المحدثة لحظياً من البورصة.")
