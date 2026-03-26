import streamlit as st
import pandas as pd
import plotly.express as px
from newsapi import NewsApiClient

# =========================
# API
# =========================
API_KEY = "6d0454ff2f7e46fe8d16e379e00f45b6"
newsapi = NewsApiClient(api_key=API_KEY)

st.set_page_config(layout="wide")

# =========================
# 스타일
# =========================
st.markdown("""
<style>
body {background-color:#0f172a;color:white;}
.header {font-size:28px;font-weight:700;margin-bottom:10px;}
.kpi {background:linear-gradient(135deg,#1e293b,#0f172a);padding:20px;border-radius:14px;text-align:center;}
.card {background:#1e293b;border-radius:14px;padding:12px;margin-bottom:15px;}
.card img {width:100%;height:180px;object-fit:cover;border-radius:10px;}
.title {font-size:15px;font-weight:600;margin-top:8px;}
.desc {font-size:12px;color:#cbd5e1;}
.link {font-size:12px;color:#38bdf8;}
</style>
""", unsafe_allow_html=True)

# =========================
# 키워드 (고정)
# =========================
KEYWORD = "병원 OR 피부미용 OR 재생의학"

st.markdown("<div class='header'>📊 AI 뉴스 BI 대시보드</div>", unsafe_allow_html=True)

# =========================
# 뉴스 조회
# =========================
data = newsapi.get_everything(
    q=KEYWORD,
    language="en",
    sort_by="publishedAt",
    page_size=50
)

df = pd.DataFrame(data["articles"])

if df.empty:
    st.warning("데이터 없음")
    st.stop()

df["publishedAt"] = pd.to_datetime(df["publishedAt"])
df["hour"] = df["publishedAt"].dt.hour
df["source"] = df["source"].apply(lambda x: x["name"])

# =========================
# 국내 언론 필터
# =========================
KOREA_DOMAINS = [
    "yna.co.kr", "chosun.com", "joongang.co.kr", "donga.com",
    "hani.co.kr", "khan.co.kr", "mk.co.kr", "hankyung.com",
    "naver.com", "daum.net", "newsis.com", "segye.com",
    "etnews.com", "mt.co.kr", "fnnews.com", "ytn.co.kr",
    "kbs.co.kr", "mbc.co.kr", "sbs.co.kr"
]

df = df[df["url"].str.contains("|".join(KOREA_DOMAINS), na=False)]

if df.empty:
    st.warning("국내 뉴스 없음")
    st.stop()

# =========================
# KPI
# =========================
col1, col2, col3 = st.columns(3)

col1.markdown(f"<div class='kpi'>총 뉴스<h2>{len(df)}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi'>언론사<h2>{df['source'].nunique()}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='kpi'>최신<h2>{df['publishedAt'].max().strftime('%H:%M')}</h2></div>", unsafe_allow_html=True)

# =========================
# 그래프
# =========================
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df, x="hour", nbins=24, title="시간대별 뉴스")
    fig.update_layout(height=300, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    top = df["source"].value_counts().head(8)
    fig2 = px.bar(top, x=top.index, y=top.values, title="언론사 TOP")
    fig2.update_layout(height=300, template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# =========================
# 뉴스 리스트
# =========================
st.markdown("## 📰 뉴스 리스트")

cols = st.columns(3)

for i, row in df.iterrows():
    with cols[i % 3]:

        img = row["urlToImage"] if row["urlToImage"] else "https://via.placeholder.com/300"

        st.markdown(f"""
        <div class="card">
            <img src="{img}">
            <div class="title">{row['title']}</div>
            <div class="desc">{row['description'] if row['description'] else ''}</div>
            <a class="link" href="{row['url']}" target="_blank">기사 보기 →</a>
        </div>
        """, unsafe_allow_html=True)
