import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

st.set_page_config(page_title="뉴스 자동 리포트", layout="wide")

st.title("🧠 바이오/의료 뉴스 자동 리포트")

# ------------------------
# 설정
# ------------------------
KEYWORD = st.text_input("키워드", "재생의학")
MAX_ITEMS = 10

# ------------------------
# 뉴스 가져오기 (네이버 RSS)
# ------------------------
def get_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    res = requests.get(url)
    root = ET.fromstring(res.content)

    items = []
    for item in root.findall(".//item")[:MAX_ITEMS]:
        title = item.find("title").text
        link = item.find("link").text
        pub_date = item.find("pubDate").text

        items.append({
            "title": title,
            "link": link,
            "date": pub_date
        })
    return items

# ------------------------
# 간단 요약 (앞부분 잘라쓰기)
# ------------------------
def summarize(text):
    return text[:80] + "..." if len(text) > 80 else text

# ------------------------
# 버튼
# ------------------------
if st.button("🔄 새로고침"):
    st.rerun()

news_list = get_news(KEYWORD)

st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ------------------------
# 통계 영역 (BI 느낌)
# ------------------------
col1, col2, col3 = st.columns(3)

col1.metric("총 뉴스 수", len(news_list))
col2.metric("키워드", KEYWORD)
col3.metric("데이터 상태", "정상")

st.markdown("---")

# ------------------------
# 뉴스 카드 UI
# ------------------------
for news in news_list:
    with st.container():
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/21/21601.png", width=80)

        with col2:
            st.subheader(news["title"])
            st.caption(news["date"])
            st.write(summarize(news["title"]))
            st.markdown(f"[▶ 기사 보기]({news['link']})")

        st.markdown("---")