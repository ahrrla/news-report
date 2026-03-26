import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(layout="wide")

# =========================
# 스타일 (연구소 느낌)
# =========================
st.markdown("""
<style>
body {
    background-color:#f5f7fb;
}

/* 상단 */
.header {
    background: linear-gradient(90deg, #1e3a8a, #2563eb);
    padding:20px;
    border-radius:12px;
    color:white;
    margin-bottom:20px;
}

/* 카드 */
.card {
    background:white;
    padding:15px;
    border-radius:10px;
    box-shadow:0 2px 8px rgba(0,0,0,0.08);
}

/* 리스트 */
.news-row {
    display:flex;
    background:white;
    border-radius:10px;
    padding:15px;
    margin-bottom:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);
}

.news-text {
    flex:3;
}

.news-title {
    font-size:16px;
    font-weight:700;
    margin-bottom:5px;
}

.news-desc {
    font-size:13px;
    color:#666;
}

.news-img {
    flex:1;
    text-align:right;
}

.news-img img {
    width:140px;
    height:90px;
    object-fit:cover;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 헤더 (핵심 복구)
# =========================
st.markdown(f"""
<div class="header">
    <h2>🧬 재생의학연구소 뉴스 인사이트</h2>
    <p>Last Update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
</div>
""", unsafe_allow_html=True)

# =========================
# 뉴스 가져오기
# =========================
def get_news():
    url = "https://news.google.com/rss/search?q=병원+피부미용+재생의학&hl=ko&gl=KR&ceid=KR:ko"
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

    return "https://via.placeholder.com/150"

df = get_news()

# =========================
# 대시보드 (복구)
# =========================
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="card">
        <h4>총 뉴스 수</h4>
        <h2>{len(df)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <h4>최신 시간</h4>
        <h2>{df.iloc[0]['date'][:16]}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# 리스트 (핵심)
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
