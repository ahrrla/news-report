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
# 🔥 본문 크롤링 (이미지 + 텍스트)
# ------------------------
def crawl_article(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        # 이미지 우선 추출
        img = soup.find("meta", property="og:image")
        if img and img.get("content"):
            image = img["content"]
        else:
            img_tag = soup.find("img")
            image = img_tag["src"] if img_tag else None

        # 본문 텍스트
        p_tags = soup.find_all("p")
        text = " ".join([p.get_text() for p in p_tags])
        text = text[:200] if text else ""

        return image, text

    except:
        return None, ""

# ------------------------
# RSS description 이미지 fallback
# ------------------------
def extract_image(description):
    try:
        img_url = re.search(r'<img src="(.*?)"', description).group(1)
        return img_url
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
        link = item.find("link").text
        pub_date = item.find("pubDate").text
        description = item.find("description").text

        # 1차: 본문 크롤링
        image, text = crawl_article(link)

        # 2차 fallback
        if not image:
            image = extract_image(description)

        # 3차 fallback
        if not image:
            image = "https://picsum.photos/400/250"

        items.append({
            "title": title,
            "link": link,
            "date": pub_date,
            "image": image,
            "text": text
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
# 📊 그래프 개선
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
    fig = px.histogram(
        df,
        x="hour",
        nbins=24,
        title="시간대별 뉴스",
        template="plotly_white"
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

with colB:
    fig2 = px.pie(
        names=["키워드 포함", "기타"],
        values=[keyword_count, len(news_list)-keyword_count],
        title="키워드 비율",
        hole=0.4
    )
    fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ------------------------
# 📰 카드 UI 개선
# ------------------------
for news in news_list:
    st.markdown(
        f"""
        <div style="
            display:flex;
            gap:20px;
            margin-bottom:25px;
            border:1px solid #e5e7eb;
            padding:18px;
            border-radius:12px;
            box-shadow:0 4px 12px rgba(0,0,0,0.06);
            background:white;
        ">
            <img src="{news['image']}" style="
                width:220px;
                height:140px;
                object-fit:cover;
                border-radius:8px;
            ">
            <div style="flex:1">
                <h4 style="margin:0 0 8px 0;">{news['title']}</h4>
                <p style="color:#6b7280; font-size:13px; margin-bottom:8px;">
                    {time_ago(news['date'])}
                </p>
                <p style="font-size:14px; color:#374151; margin-bottom:10px;">
                    {news['text'] if news['text'] else "본문 요약 없음"}
                </p>
                <a href="{news['link']}" target="_blank" style="
                    color:#2563eb;
                    font-weight:600;
                    text-decoration:none;
                ">▶ 기사 보기</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
