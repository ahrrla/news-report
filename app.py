import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from newsapi import NewsApiClient

# =========================
# API KEY
# =========================
API_KEY = "6d0454ff2f7e46fe8d16e379e00f45b6"
newsapi = NewsApiClient(api_key=API_KEY)

st.set_page_config(layout="wide")

# =========================
# 스타일 (대시보드 느낌)
# =========================
st.markdown("""
<style>
body {background-color: #0e1117; color: white;}
.kpi {background:#1c1f26;padding:20px;border-radius:12px;text-align:center;}
.card {background:#1c1f26;padding:15px;border-radius:12px;margin-bottom:15px;}
.card img {width:100%;border-radius:10px;}
.title {font-size:15px;font-weight:600;margin-top:10px;}
</style>
""", unsafe_allow_html=True)

# =========================
# 검색
# =========================
keyword = st.text_input("키워드", "MES")

data = newsapi.get_everything(
    q=keyword,
    language="ko",
    sort_by="publishedAt",
    page_size=50
)

df = pd.DataFrame(data["articles"])

if df.empty:
    st.warning("데이터 없음")
    st.stop()

df["publishedAt"] = pd.to_datetime(df["publishedAt"])
df["hour"] = df["publishedAt"].dt.hour
df["date"] = df["publishedAt"].dt.date
df["source"] = df["source"].apply(lambda x: x["name"])

# =========================
# KPI
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"<div class='kpi'>총 뉴스<h2>{len(df)}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi'>키워드<h2>{keyword}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='kpi'>언론사<h2>{df['source'].nunique()}</h2></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='kpi'>최신<h2>{df['publishedAt'].max().strftime('%H:%M')}</h2></div>", unsafe_allow_html=True)

# =========================
# 그래프 1 - 시간대
# =========================
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df, x="hour", nbins=24, title="시간대별 뉴스 발생")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# 그래프 2 - 언론사 TOP
# =========================
with col2:
    top = df["source"].value_counts().head(10)
    fig2 = px.bar(top, x=top.index, y=top.values, title="언론사 TOP10")
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# =========================
# 그래프 3 - 트렌드
# =========================
trend = df.groupby("date").size().reset_index(name="count")

fig3 = px.line(trend, x="date", y="count", title="날짜별 뉴스 트렌드")
fig3.update_layout(template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

# =========================
# 그래프 4 - 도넛
# =========================
fig4 = go.Figure(data=[go.Pie(
    labels=top.index,
    values=top.values,
    hole=.5
)])
fig4.update_layout(template="plotly_dark", title="뉴스 비율")
st.plotly_chart(fig4, use_container_width=True)

# =========================
# 뉴스 카드
# =========================
st.markdown("## 뉴스 리스트")

cols = st.columns(3)

for i, row in df.iterrows():
    with cols[i % 3]:
        img = row["urlToImage"] if row["urlToImage"] else "https://via.placeholder.com/300"

        st.markdown(f"""
        <div class="card">
            <img src="{img}">
            <div class="title">{row['title']}</div>
            <a href="{row['url']}" target="_blank">기사 보기</a>
        </div>
        """, unsafe_allow_html=True)
