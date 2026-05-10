import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="بورصة الوحيد Pro", layout="wide")

# تصميم N-CURE الاحترافي
st.markdown("""
    <style>
    .stApp { background-color: #000022; color: white; }
    .header { background: #1a6b3c; padding: 20px; text-align: center; border-radius: 0 0 20px 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header"><h1>📊 منصة الوحيد للتحليل المباشر</h1></div>', unsafe_allow_html=True)

# إضافة Widget من TradingView للسوق المصري
st.write("### 📈 متابعة السوق المصري لحظياً")

# هذا الكود يقوم بعرض شارت TradingView الأصلي داخل تطبيقك
tradingview_html = """
<div class="tradingview-widget-container" style="height:600px;">
  <div id="tradingview_12345" style="height:calc(100% - 32px);"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true,
    "symbol": "EGX:COMI",
    "interval": "D",
    "timezone": "Africa/Cairo",
    "theme": "dark",
    "style": "1",
    "locale": "ar",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_12345"
  });
  </script>
</div>
"""

components.html(tradingview_html, height=650)

st.info("💡 يمكنك تغيير رمز السهم من داخل الشارت مباشرة (مثلاً اكتب FWRY أو TMGH).")
