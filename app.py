import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from dateutil import parser
import pandas as pd
from bs4 import BeautifulSoup
import plotly.express as px
import re

st.set_page_config(page_title="뉴스 BI 대시보드", layout="wide")

# ------------------------
# 🎨 상단 스타일 (대시보드 느낌)
# ------------------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background: linear-gradient(135deg, #1e3a5f, #0f172a);
    padding: 20px;
    border-radius: 15px;
    color: white;
}
.metric-title {
    font-size: 14px;
    opacity: 0.7;
}
.metric-value {
    font-size: 32px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🧠 바이오/의료 뉴스 BI 대시보드")

KEYWORD = st.text_input("키워드", "재생의학")

# ------------------------
# 시간 변환
# ------------------------
def time_ago(pub_date):
    dt = parser.parse(pub_date)
    now = datetime.now(timezone.utc)
    diff = now - dt
    minutes = int(diff.total_seconds() / 60)
    hours = int(minutes / 60)

    if minutes < 60:
        return f"{minutes}분 전"
    elif hours < 24:
        return f"{hours}시간 전"
    else:
        return f"{int(hours/24)}일 전"

# ------------------------
# 🔥 RSS description → 실제 기사 링크 추출 (핵심 해결)
# ------------------------
def extract_real_link(description):
    try:
        soup = BeautifulSoup(description, "html.parser")
        a = soup.find("a")
        return a["href"]
    except:
        return None

# ------------------------
# 🔥 이미지 추출 (최종 안정버전)
# ------------------------
def get_image(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        # og:image
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]

        # 본문 이미지
        imgs = soup.find_all("img")
        for img in imgs:
            src = img.get("src")
            if src and "http" in src and "logo" not in src:
                return src

        return None
    except:
        return None

# ------------------------
# 뉴스 수집
# ------------------------
def get_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    res = requests.get(url)
    root = ET.fromstring(res.content)

    items = []
    for item in root.findall(".//item")[:10]:
        title = item.find("title").text
        pub_date = item.find("pubDate").text
        description = item.find("description").text

        real_link = extract_real_link(description)

        image = get_image(real_link) if real_link else None

        if not image:
            try:
                image = re.search(r'<img src="(.*?)"', description).group(1)
            except:
                image = "https://picsum.photos/400/250"

        items.append({
            "title": title,
            "link": real_link,
            "date": pub_date,
            "image": image
        })

    return items

news_list = get_news(KEYWORD)

# ------------------------
# KPI 카드
# ------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">총 뉴스</div>
        <div class="metric-value">{len(news_list)}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">키워드</div>
        <div class="metric-value">{KEYWORD}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">상태</div>
        <div class="metric-value">정상</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ------------------------
# 📊 그래프 (대시보드 스타일)
# ------------------------
times = []
for n in news_list:
    try:
        dt = parser.parse(n["date"])
        times.append(dt.hour)
    except:
        pass

df = pd.DataFrame(times, columns=["시간"])

keyword_count = sum(1 for n in news_list if KEYWORD in n["title"])

colA, colB = st.columns(2)

with colA:
    fig = px.histogram(df, x="시간", nbins=24)
    fig.update_layout(
        title="시간대별 뉴스",
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font_color="white",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True)
    )
    st.plotly_chart(fig, use_container_width=True)

with colB:
    fig2 = px.pie(
        names=["키워드 포함", "기타"],
        values=[keyword_count, len(news_list)-keyword_count],
        hole=0.5
    )
    fig2.update_layout(
        title="키워드 비율",
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font_color="white"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ------------------------
# 📰 뉴스 카드
# ------------------------
for news in news_list:
    st.markdown(f"""
    <div style="
        display:flex;
        gap:20px;
        margin-bottom:20px;
        padding:15px;
        border-radius:10px;
        background:#1e293b;
        color:white;
    ">
        <img src="{news['image']}" width="200" style="border-radius:8px;">
        <div>
            <h4>{news['title']}</h4>
            <p style="color:#94a3b8">{time_ago(news['date'])}</p>
            <a href="{news['link']}" target="_blank" style="color:#60a5fa;">▶ 기사 보기</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
