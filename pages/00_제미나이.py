import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="Global Stock Viewer", layout="wide")

st.title("📈 한·미 주요 주식 수익률 비교 대시보드")
st.sidebar.header("설정")

# 1. 비교할 주식 리스트 설정 (한국은 .KS / .KQ 필수)
stock_dict = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "NAVER": "035420.KS",
    "에코프로": "086520.KQ",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Microsoft": "MSFT",
    "S&P 500 (ETF)": "SPY",
    "KOSPI 200 (ETF)": "069500.KS"
}

# 2. 사이드바 인터페이스
selected_stocks = st.sidebar.multiselect(
    "비교할 종목을 선택하세요", 
    list(stock_dict.keys()), 
    default=["삼성전자", "Apple", "NVIDIA"]
)

period = st.sidebar.selectbox(
    "조회 기간", 
    ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], 
    index=3
)

if not selected_stocks:
    st.warning("종목을 하나 이상 선택해주세요!")
else:
    # 3. 데이터 불러오기
    tickers = [stock_dict[s] for s in selected_stocks]
    data = yf.download(tickers, period=period)['Close']
    
    # 데이터가 1개일 경우 Series로 반환되므로 DataFrame으로 변환
    if len(selected_stocks) == 1:
        data = data.to_frame()
        data.columns = selected_stocks
    else:
        # 컬럼명을 티커에서 한글 이름으로 변경
        inv_dict = {v: k for k, v in stock_dict.items()}
        data.columns = [inv_dict[col] for col in data.columns]

    # 4. 수익률 계산 (첫날 가격을 100으로 기준점 통일)
    st.subheader("🚀 기준일 대비 수익률 비교 (Normalized)")
    norm_data = (data / data.iloc[0]) * 100
    
    fig_norm = go.Figure()
    for col in norm_data.columns:
        fig_norm.add_trace(go.Scatter(x=norm_data.index, y=norm_data[col], name=col, mode='lines'))
    
    fig_norm.update_layout(
        hovermode="x unified",
        yaxis_title="수익률 (기준=100)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_norm, use_container_width=True)

    # 5. 종가 차트 (개별 가격)
    st.subheader("💰 주가 흐름 (Closing Price)")
    fig_price = go.Figure()
    for col in data.columns:
        fig_price.add_trace(go.Scatter(x=data.index, y=data[col], name=col, mode='lines'))
        
    fig_price.update_layout(
        hovermode="x unified",
        yaxis_title="주가 (각국 통화 기준)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # 6. 데이터 표 출력
    with st.expander("최근 데이터 확인"):
        st.dataframe(data.tail())
