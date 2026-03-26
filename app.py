import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from dateutil import parser
import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'

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
# 📊 데이터 가공
# ------------------------
times = []
for n in news_list:
    try:
        dt = parser.parse(n["date"])
        times.append(dt.hour)
    except:
        pass

df = pd.DataFrame(times, columns=["hour"])
chart_data = df["hour"].value_counts().sort_index()

keyword_count = sum(1 for n in news_list if KEYWORD in n["title"])

# ------------------------
# 📊 그래프 영역
# ------------------------
colA, colB = st.columns(2)

# 시간대별 그래프
with colA:
    st.subheader("📊 시간대별 뉴스 발생 현황")

    if not df.empty:
        fig, ax = plt.subplots()
        chart_data.plot(kind='bar', ax=ax)

        ax.set_xlabel("시간 (시)")
        ax.set_ylabel("뉴스 건수")
        ax.set_title("시간대별 뉴스 분포")

        plt.xticks(rotation=0)

        st.pyplot(fig)

# 키워드 비율 그래프
with colB:
    st.subheader("📊 키워드 포함 비율")

    fig2, ax2 = plt.subplots()

    labels = ["키워드 포함", "기타"]
    values = [keyword_count, len(news_list) - keyword_count]

    ax2.bar(labels, values)

    ax2.set_xlabel("구분")
    ax2.set_ylabel("건수")
    ax2.set_title("키워드 포함 여부")

    plt.xticks(rotation=0)

    st.pyplot(fig2)

st.markdown("---")

# ------------------------
# 📰 뉴스 카드
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
