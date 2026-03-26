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

st.title("🧠 바이오/의료 뉴스 BI 대시보드")

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
# 🔥 Google 뉴스 → 실제 기사 URL 변환
# ------------------------
def get_real_url(google_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(google_url, headers=headers, allow_redirects=True, timeout=5)
        return res.url
    except:
        return google_url

# ------------------------
# 🔥 본문 이미지 추출 (핵심 수정)
# ------------------------
def get_article_image(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        # 1순위: og:image
        og = soup.find("meta", property="og:image")
        if og and og.get("content") and "google" not in og["content"]:
            return og["content"]

        # 2순위: twitter:image
        tw = soup.find("meta", property="twitter:image")
        if tw and tw.get("content") and "google" not in tw["content"]:
            return tw["content"]

        # 실패
        return None
    except:
        return None

# ------------------------
# RSS description fallback
# ------------------------
def extract_image(description):
    try:
        img_url = re.search(r'<img src="(.*?)"', description).group(1)
        if "google" not in img_url:
            return img_url
        return None
    except:
        return None

# ------------------------
# 뉴스 수집 (핵심 로직 수정)
# ------------------------
def get_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    res = requests.get(url)
    root = ET.fromstring(res.content)

    items = []
    for item in root.findall(".//item")[:10]:
        title = item.find("title").text
        google_link = item.find("link").text
        pub_date = item.find("pubDate").text
        description = item.find("description").text

        # 👉 실제 기사 URL 가져오기
        real_link = get_real_url(google_link)

        # 👉 본문 이미지 크롤링
        image = get_article_image(real_link)

        # 👉 fallback
        if not image:
            image = extract_image(description)

        if not image:
            image = "https://picsum.photos/400/250"

        items.append({
            "title": title,
            "link": real_link,
            "date": pub_date,
            "image": image
        })

    return items

if st.button("🔄 새로고침"):
    st.rerun()

news_list = get_news(KEYWORD)

# ------------------------
# KPI
# ------------------------
col1, col2, col3 = st.columns(3)

col1.metric("총 뉴스 수", len(news_list))
col2.metric("키워드", KEYWORD)
col3.metric("상태", "정상")

st.markdown("---")

# ------------------------
# 📊 그래프 (건드리지 않음)
# ------------------------
times = []
for n in news_list:
    try:
        dt = parser.parse(n["date"])
        times.append(dt.hour)
    except:
        pass

df = pd.DataFrame(times, columns=["hour"])

keyword_count = sum(1 for n in news_list if KEYWORD in n["title"])

colA, colB = st.columns(2)

with colA:
    fig = px.histogram(df, x="hour", nbins=24,
                       title="시간대별 뉴스")
    st.plotly_chart(fig, use_container_width=True)

with colB:
    fig2 = px.pie(
        names=["키워드 포함", "기타"],
        values=[keyword_count, len(news_list)-keyword_count],
        title="키워드 비율"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ------------------------
# 📰 뉴스 카드 (그대로 유지)
# ------------------------
for news in news_list:
    st.markdown(
        f"""
        <div style="display:flex; gap:20px; margin-bottom:20px;
                    border:1px solid #eee; padding:15px; border-radius:10px;
                    box-shadow:2px 2px 10px rgba(0,0,0,0.05)">
            <img src="{news['image']}" width="200">
            <div>
                <h4>{news['title']}</h4>
                <p style="color:gray">{time_ago(news['date'])}</p>
                <a href="{news['link']}" target="_blank">▶ 기사 보기</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
