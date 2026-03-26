import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="주식 비교 분석", layout="wide")

st.title("📊 한국 vs 미국 주식 비교 분석")

# ---------------------------
# 입력 영역
# ---------------------------
st.sidebar.header("📌 설정")

korea_stock = st.sidebar.text_input("한국 주식 티커 (예: 005930.KS)", "005930.KS")
us_stock = st.sidebar.text_input("미국 주식 티커 (예: AAPL)", "AAPL")

period = st.sidebar.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3
)

# ---------------------------
# 데이터 불러오기
# ---------------------------
@st.cache_data
def load_data(ticker, period):
    data = yf.download(ticker, period=period)
    return data

korea_data = load_data(korea_stock, period)
us_data = load_data(us_stock, period)

# ---------------------------
# 데이터 확인
# ---------------------------
if korea_data.empty or us_data.empty:
    st.error("⚠️ 티커를 다시 확인해주세요!")
    st.stop()

# ---------------------------
# 수익률 계산
# ---------------------------
def calc_return(data):
    return (data["Close"][-1] / data["Close"][0] - 1) * 100

korea_return = calc_return(korea_data)
us_return = calc_return(us_data)

# ---------------------------
# 수익률 표시
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.metric(f"🇰🇷 {korea_stock} 수익률", f"{korea_return:.2f}%")

with col2:
    st.metric(f"🇺🇸 {us_stock} 수익률", f"{us_return:.2f}%")

# ---------------------------
# 가격 차트
# ---------------------------
st.subheader("📈 가격 비교")

fig, ax = plt.subplots()
ax.plot(korea_data.index, korea_data["Close"], label=korea_stock)
ax.plot(us_data.index, us_data["Close"], label=us_stock)
ax.legend()
ax.set_xlabel("Date")
ax.set_ylabel("Price")
st.pyplot(fig)

# ---------------------------
# 정규화 차트
# ---------------------------
st.subheader("📊 정규화 비교 (시작 = 100)")

korea_norm = korea_data["Close"] / korea_data["Close"].iloc[0] * 100
us_norm = us_data["Close"] / us_data["Close"].iloc[0] * 100

fig2, ax2 = plt.subplots()
ax2.plot(korea_norm.index, korea_norm, label=korea_stock)
ax2.plot(us_norm.index, us_norm, label=us_stock)
ax2.legend()
ax2.set_xlabel("Date")
ax2.set_ylabel("Normalized Price")
st.pyplot(fig2)

# ---------------------------
# 데이터 테이블
# ---------------------------
st.subheader("📋 데이터 보기")

st.write("한국 주식")
st.dataframe(korea_data.tail())

st.write("미국 주식")
st.dataframe(us_data.tail())
