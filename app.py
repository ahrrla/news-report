import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import time

st.set_page_config(layout="wide")

# =========================
# 스타일 (기존 유지 + 시간만 개선)
# =========================
st.markdown("""
<style>

/* 시간 강조 */
.live-time {
    font-size:28px;
    font-weight:700;
    color:#38bdf8;
    margin-top:10px;
}

/* 모바일 가독성 보정 (최소 수정) */
.news-title {
    color:#ffffff !important;
}

.news-desc {
    color:#cbd5f5 !important;
}

a {
    color:#38bdf8 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 키워드 입력
# =========================
keyword = st.text_input("🔍 키워드 입력", "병원 피부미용 재생의학")

# =========================
# 실시간 시간
# =========================
time_placeholder = st.empty()

# =========================
# 헤더 (기존 유지)
# =========================
st.markdown(f"""
<div class="header">
    <h2>🧬 재생의학연구소 뉴스 인사이트</h2>
    <p>현재 키워드: <b>{keyword}</b></p>
</div>
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
# KPI (기존 그대로)
# =========================
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="kpi">
        <h4>총 뉴스 수</h4>
        <h1>{len(df)}</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi">
        <h4>최신 기사 시간</h4>
        <h2>{df.iloc[0]['date'][:16]}</h2>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 실시간 시간 표시 (핵심 개선)
# =========================
while True:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    time_placeholder.markdown(f"""
    <div class="live-time">⏰ 현재 시간: {now}</div>
    """, unsafe_allow_html=True)

    time.sleep(1)

# =========================
# 리스트 (기존 유지)
# =========================
st.subheader("📄 뉴스 리스트")

for _, row in df.iterrows():

    img = get_img(row["link"])

    st.markdown(f"""
    <div class="news-row">
        <div class="news-text">
            <div class="news-title">{row['title']}</div>
            <div class="news-desc">{row['date']}</div>
            <a href="{row['link']}" target="_blank">기사보기 →</a>
        </div>
        <div class="news-img">
            <img src="{img}">
        </div>
    </div>
    """, unsafe_allow_html=True)
