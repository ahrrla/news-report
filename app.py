import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from dateutil import parser
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

plt.rcParams['font.family'] = 'Malgun Gothic'

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
# 기사 이미지 가져오기
# ------------------------
def get_image(url):
    try:
        res = requests.get(url, timeout=3)
        soup = BeautifulSoup(res.text, "html.parser")

        img = soup.find("meta", property="og:image")
        if img:
            return img["content"]
    except:
        pass

    return "https://picsum.photos/400/250"

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

        image = get_image(link)

        items.append({
            "title": title,
            "link": link,
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
# 뉴스 UI
# ------------------------
for news in news_list:
    col1, col2 = st.columns([1,3])

    with col1:
        st.image(news["image"], use_container_width=True)

    with col2:
        st.subheader(news["title"])
        st.caption(time_ago(news["date"]))
        st.markdown(f"[▶ 기사 보기]({news['link']})")

    st.markdown("---")
