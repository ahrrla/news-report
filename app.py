import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import plotly.express as px

st.set_page_config(layout="wide")

# =========================
# 스타일
# =========================
st.markdown("""
<style>
body {background:#0f172a;color:white;}
.header {font-size:28px;font-weight:700;margin-bottom:10px;}
.kpi {background:#1e293b;padding:20px;border-radius:14px;text-align:center;}
.card {background:#1e293b;padding:12px;border-radius:14px;margin-bottom:15px;}
.card img {width:100%;height:180px;object-fit:cover;border-radius:10px;}
.title {font-size:15px;font-weight:600;margin-top:8px;}
.desc {font-size:12px;color:#cbd5e1;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>📊 AI 뉴스 BI 대시보드</div>", unsafe_allow_html=True)

# =========================
# RSS 뉴스 가져오기
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
# 이미지 가져오기
# =========================
def get_image(url):
    try:
        r = requests.get(url, timeout=2)
        soup = BeautifulSoup(r.text, "html.parser")

        og = soup.find("meta", property="og:image")
        if og:
            return og["content"]

    except:
        pass

    return "https://via.placeholder.com/300"

# =========================
# 실행
# =========================
df = get_news()

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
# 뉴스 리스트
# =========================
st.markdown("## 📰 뉴스 리스트")

cols = st.columns(3)

for i, row in df.iterrows():
    img = get_image(row["link"])

    with cols[i % 3]:
        st.markdown(f"""
        <div class="card">
            <img src="{img}">
            <div class="title">{row['title']}</div>
            <a href="{row['link']}" target="_blank">기사 보기 →</a>
        </div>
        """, unsafe_allow_html=True)
