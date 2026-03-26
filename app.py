import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")

# =========================
# 스타일 (리스트형)
# =========================
st.markdown("""
<style>
body {background:#0f172a;color:white;}

.news-row {
    display:flex;
    background:#1e293b;
    border-radius:12px;
    padding:15px;
    margin-bottom:12px;
    align-items:center;
}

.news-text {
    flex:3;
    padding-right:15px;
}

.news-title {
    font-size:16px;
    font-weight:700;
    margin-bottom:6px;
}

.news-desc {
    font-size:13px;
    color:#cbd5e1;
}

.news-img {
    flex:1;
}

.news-img img {
    width:100%;
    height:120px;
    object-fit:cover;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 AI 뉴스 BI 대시보드")

# =========================
# RSS
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
            "pubDate": item.pubDate.text
        })

    return pd.DataFrame(data)

# =========================
# 이미지 (핵심 개선)
# =========================
def get_image(url):
    try:
        r = requests.get(url, timeout=3)
        soup = BeautifulSoup(r.text, "html.parser")

        # og:image 우선
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]

        # fallback
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

    except:
        pass

    return "https://via.placeholder.com/150"

# =========================
# 데이터
# =========================
df = get_news()

# =========================
# 리스트 출력 (핵심)
# =========================
for _, row in df.iterrows():

    img = get_image(row["link"])

    st.markdown(f"""
    <div class="news-row">
        <div class="news-text">
            <div class="news-title">{row['title']}</div>
            <div class="news-desc">{row['pubDate']}</div>
            <a href="{row['link']}" target="_blank">기사 보기 →</a>
        </div>
        <div class="news-img">
            <img src="{img}">
        </div>
    </div>
    """, unsafe_allow_html=True)
