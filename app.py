import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from bs4 import BeautifulSoup

# =========================
# 네이버 API
# =========================
CLIENT_ID = "dmIEAMApT_Ep6C7bPNs2"
CLIENT_SECRET = "Cylzhl0oGi"

st.set_page_config(layout="wide")

# =========================
# 스타일
# =========================
st.markdown("""
<style>
body {background:#0f172a;color:white;}
.kpi {background:#1e293b;padding:20px;border-radius:14px;text-align:center;}
.card {background:#1e293b;padding:12px;border-radius:14px;margin-bottom:15px;}
.card img {width:100%;height:180px;object-fit:cover;border-radius:10px;}
.title {font-size:15px;font-weight:600;margin-top:8px;}
.desc {font-size:12px;color:#cbd5e1;}
</style>
""", unsafe_allow_html=True)

# =========================
# 뉴스 검색 함수
# =========================
def get_news():
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    params = {
        "query": "병원 피부미용 재생의학",
        "display": 30,
        "sort": "date"
    }

    res = requests.get(url, headers=headers, params=params)
    return res.json()["items"]

# =========================
# 이미지 추출 (기사 크롤링)
# =========================
def get_image(url):
    try:
        r = requests.get(url, timeout=2)
        soup = BeautifulSoup(r.text, "html.parser")

        og = soup.find("meta", property="og:image")
        if og:
            return og["content"]

        img = soup.find("img")
        if img:
            return img.get("src")

    except:
        pass

    return "https://via.placeholder.com/300"

# =========================
# 데이터
# =========================
data = get_news()

df = pd.DataFrame(data)

df["title"] = df["title"].str.replace("<b>", "").str.replace("</b>", "")
df["description"] = df["description"].str.replace("<b>", "").str.replace("</b>", "")
df["pubDate"] = pd.to_datetime(df["pubDate"])
df["hour"] = df["pubDate"].dt.hour

# =========================
# KPI
# =========================
col1, col2 = st.columns(2)

col1.markdown(f"<div class='kpi'>총 뉴스<h2>{len(df)}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi'>최신<h2>{df['pubDate'].max().strftime('%H:%M')}</h2></div>", unsafe_allow_html=True)

# =========================
# 그래프
# =========================
fig = px.histogram(df, x="hour", nbins=24, title="시간대별 뉴스")
fig.update_layout(height=300, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# =========================
# 뉴스 리스트 (개선됨)
# =========================
st.markdown("## 📰 뉴스 리스트")

cols = st.columns(3)

for i, row in df.iterrows():

    link = row["link"] if "n.news.naver.com" in row["link"] else row["originallink"]
    img = get_image(link)

    with cols[i % 3]:
        st.markdown(f"""
        <div class="card">
            <img src="{img}">
            <div class="title">{row['title']}</div>
            <div class="desc">{row['description']}</div>
            <a href="{link}" target="_blank">기사 보기 →</a>
        </div>
        """, unsafe_allow_html=True)
