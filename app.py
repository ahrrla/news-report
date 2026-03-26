import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from dateutil import parser

st.set_page_config(page_title="뉴스 리포트", layout="wide")

st.title("🧠 바이오/의료 뉴스 자동 리포트")

KEYWORD = st.text_input("키워드", "재생의학")

# ------------------------
# 시간 변환 (몇분 전)
# ------------------------
def time_ago(pub_date):
    try:
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
    except:
        return pub_date

# ------------------------
# 뉴스 가져오기 (이미지 포함)
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

        # 임시 이미지 (실제 뉴스 크롤링 없이 대체)
        img = "https://source.unsplash.com/400x250/?medical"

        items.append({
            "title": title,
            "link": link,
            "date": pub_date,
            "image": img
        })
    return items

# ------------------------
# 버튼
# ------------------------
if st.button("🔄 새로고침"):
    st.rerun()

news_list = get_news(KEYWORD)

st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ------------------------
# KPI 영역 (BI 느낌)
# ------------------------
col1, col2, col3 = st.columns(3)

col1.metric("총 뉴스 수", len(news_list))
col2.metric("키워드", KEYWORD)
col3.metric("데이터 상태", "정상")

st.markdown("---")

# ------------------------
# 카드 UI
# ------------------------
for news in news_list:
    with st.container():
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(news["image"])

        with col2:
            st.subheader(news["title"])
            st.caption(time_ago(news["date"]))
            st.markdown(f"[▶ 기사 보기]({news['link']})")

        st.markdown("---")
