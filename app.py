import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

# =========================
# 자동 새로고침 (1초)
# =========================
st_autorefresh(interval=1000, key="clock")

# =========================
# 스타일 (모바일 포함 개선)
# =========================
st.markdown("""
<style>

body {
    color:#111827;
}

.live-time {
    font-size:28px;
    font-weight:800;
    color:#1e3a8a;
    margin-bottom:10px;
}

.news-card {
    display:flex;
    justify-content:space-between;
    align-items:center;
    background:#ffffff;
    padding:14px;
    border-radius:12px;
    margin-bottom:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.1);
}

.news-left {
    width:70%;
}

.news-title {
    font-size:15px;
    font-weight:700;
    color:#111827;
}

.news-date {
    font-size:12px;
    color:#6b7280;
    margin-top:4px;
}

.news-link {
    display:inline-block;
    margin-top:6px;
    color:#2563eb;
    font-weight:600;
    font-size:13px;
}

.news-img {
    width:100px;
    height:70px;
    border-radius:8px;
}

@media (max-width:768px) {
    .news-card {
        flex-direction:column;
        align-items:flex-start;
    }
    .news-left {
        width:100%;
    }
    .news-img {
        margin-top:8px;
        width:100%;
        height:auto;
    }
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
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f'<div class="live-time">⏰ 현재 시간: {now}</div>', unsafe_allow_html=True)

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
# 이미지 가져오기
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

    return "https://via.placeholder.com/120"

df = get_news(keyword)

# =========================
# KPI
# =========================
col1, col2 = st.columns(2)

with col1:
    st.metric("총 뉴스 수", len(df))

with col2:
    st.metric("최신 기사 시간", df.iloc[0]["date"][:16])

# =========================
# 뉴스 리스트 (🔥 핵심 정상 출력)
# =========================
st.subheader("📄 뉴스 리스트")

for _, row in df.iterrows():

    title = row["title"].replace("<", "").replace(">", "")
    img = get_img(row["link"])

    st.markdown(f"""
<div class="news-card">

    <div class="news-left">
        <div class="news-title">{title}</div>
        <div class="news-date">{row['date']}</div>
        <a class="news-link" href="{row['link']}" target="_blank">기사보기 →</a>
    </div>

    <div>
        <img class="news-img" src="{img}">
    </div>

</div>
""", unsafe_allow_html=True)
