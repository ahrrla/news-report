import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(layout="wide")

# =========================
# 스타일
# =========================
st.markdown("""
<style>

/* 시간 색상 (어둡게 변경) */
.live-time {
    font-size:26px;
    font-weight:700;
    color:#2563eb;
    margin-bottom:10px;
}

/* 모바일 가독성 */
.news-title {
    color:#111827 !important;
}

.news-desc {
    color:#4b5563 !important;
}

a {
    color:#2563eb !important;
    font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 키워드 입력
# =========================
keyword = st.text_input("🔍 키워드 입력", "병원 피부미용 재생의학")

# =========================
# 현재 시간 (한번만 표시)
# =========================
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f"""
<div class="live-time">⏰ 현재 시간: {now}</div>
""", unsafe_allow_html=True)

# =========================
# 헤더
# =========================
st.markdown(f"""
<h2>🧬 재생의학연구소 뉴스 인사이트</h2>
<p>현재 키워드: <b>{keyword}</b></p>
""", unsafe_allow_html=True)

# =========================
# 뉴스 가져오기
# =========================
def get_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "xml")

    items = soup.find_all("item")

    data = []
    for item in items:
        data.append({
            "title": item.title.text,
            "link": item.link.text,
            "date": item.pubDate.text
        })

    return pd.DataFrame(data)

# =========================
# 이미지
# =========================
def get_img(url):
    try:
        r = requests.get(url, timeout=3)
        soup = BeautifulSoup(r.text, "html.parser")

        og = soup.find("meta", property="og:image")
        if og:
            return og["content"]
    except:
        pass

    return "https://via.placeholder.com/150"

df = get_news(keyword)

# =========================
# KPI
# =========================
col1, col2 = st.columns(2)

with col1:
    st.metric("총 뉴스 수", len(df))

with col2:
    st.metric("최신 기사 시간", df.iloc[0]['date'][:16])

# =========================
# 리스트 (복구됨)
# =========================
st.subheader("📄 뉴스 리스트")

for _, row in df.iterrows():

    img = get_img(row["link"])

    st.markdown(f"""
    <div style="display:flex; background:#ffffff; padding:15px; border-radius:10px; margin-bottom:10px; box-shadow:0 2px 6px rgba(0,0,0,0.08);">
        
        <div style="flex:3;">
            <div class="news-title">{row['title']}</div>
            <div class="news-desc">{row['date']}</div>
            <a href="{row['link']}" target="_blank">기사보기 →</a>
        </div>

        <div style="flex:1; text-align:right;">
            <img src="{img}" style="width:120px; height:80px; border-radius:8px;">
        </div>

    </div>
    """, unsafe_allow_html=True)
