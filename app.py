import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from dateutil import parser
import pandas as pd

st.set_page_config(page_title="뉴스 BI 대시보드", layout="wide")

st.title("🧠 바이오/의료 뉴스 BI 대시보드")

KEYWORD = st.text_input("키워드", "재생의학")

# ------------------------
# 시간 변환
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
# 뉴스 수집
# ------------------------
def get_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    res = requests.get(url)
    root = ET.fromstring(res.content)

    items = []
    for item in root.findall(".//item")[:15]:
        title = item.find("title").text
        link = item.find("link").text
        pub_date = item.find("pubDate").text

        img = "https://picsum.photos/400/250"

        items.append({
            "title": title,
            "link": link,
            "date": pub_date,
            "image": img
        })
    return items

if st.button("🔄 새로고침"):
    st.rerun()

news_list = get_news(KEYWORD)

st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ------------------------
# KPI 영역
# ------------------------
col1, col2, col3 = st.columns(3)

col1.metric("총 뉴스 수", len(news_list))
col2.metric("키워드", KEYWORD)
col3.metric("데이터 상태", "정상")

st.markdown("---")

# ------------------------
# 📊 BI 차트 영역
# ------------------------

# 시간별 뉴스 개수
times = []
for n in news_list:
    try:
        dt = parser.parse(n["date"])
        hour = dt.hour
        times.append(hour)
    except:
        pass

df = pd.DataFrame(times, columns=["hour"])

if not df.empty:
    chart_data = df["hour"].value_counts().sort_index()

    st.subheader("📊 시간대별 뉴스 발생 분포")
    st.bar_chart(chart_data)

# 키워드 포함 여부 간단 통계
keyword_count = sum(1 for n in news_list if KEYWORD in n["title"])

pie_df = pd.DataFrame({
    "구분": ["키워드 포함", "기타"],
    "개수": [keyword_count, len(news_list) - keyword_count]
}).set_index("구분")

st.subheader("📊 키워드 포함 비율")
st.bar_chart(pie_df)

st.markdown("---")

# ------------------------
# 📰 뉴스 카드 UI
# ------------------------
st.subheader("📰 뉴스 리스트")

for news in news_list:
    with st.container():
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(news["image"], use_container_width=True)

        with col2:
            st.subheader(news["title"])
            st.caption(time_ago(news["date"]))
            st.markdown(f"[▶ 기사 보기]({news['link']})")

        st.markdown("---")
