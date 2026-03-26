import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Noto+Sans+KR:wght@300;400;700&display=swap');

:root {
    --bg-primary:   #0a0e1a;
    --bg-card:      #111827;
    --bg-card2:     #1a2236;
    --accent-green: #00ff9d;
    --accent-red:   #ff4d6d;
    --accent-blue:  #4d8cff;
    --accent-gold:  #ffd166;
    --text-main:    #e8eaf0;
    --text-muted:   #6b7a99;
    --border:       #1f2d45;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-main);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
    color: var(--text-main) !important;
}

/* Hide default header */
header[data-testid="stHeader"] { background: transparent; }

/* Metric cards */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: border-color .2s;
}
.metric-card:hover { border-color: var(--accent-blue); }
.metric-title {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: var(--text-main);
}
.metric-delta-pos { color: var(--accent-green); font-size: 13px; }
.metric-delta-neg { color: var(--accent-red);   font-size: 13px; }

/* Section title */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent-gold);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
}

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0d1f3c 0%, #0a0e1a 60%, #0d2b1f 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,255,157,.08) 0%, transparent 70%);
}
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 4px 0;
}
.hero-sub {
    color: var(--text-muted);
    font-size: 14px;
    margin: 0;
}
.hero-badge {
    display: inline-block;
    background: rgba(0,255,157,.12);
    color: var(--accent-green);
    border: 1px solid rgba(0,255,157,.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 11px;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

/* Tag chips */
.tag {
    display: inline-block;
    background: rgba(77,140,255,.12);
    color: var(--accent-blue);
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 12px;
    margin: 2px;
}
.tag-kr { background: rgba(255,209,102,.1); color: var(--accent-gold); }

/* Streamlit element overrides */
div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label,
div[data-testid="stSlider"] label,
div[data-testid="stDateInput"] label { color: var(--text-muted) !important; font-size: 12px; }

div[data-testid="stTabs"] button {
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    letter-spacing: 1px;
}

/* Plotly chart background fix */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Stock Universe ────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자":     "005930.KS",
    "SK하이닉스":   "000660.KS",
    "LG에너지솔루션":"373220.KS",
    "현대차":       "005380.KS",
    "POSCO홀딩스":  "005490.KS",
    "NAVER":        "035420.KS",
    "카카오":       "035720.KS",
    "셀트리온":     "068270.KS",
    "삼성바이오로직스":"207940.KS",
    "기아":         "000270.KS",
    "KB금융":       "105560.KS",
    "신한지주":     "055550.KS",
    "LG화학":       "051910.KS",
    "롯데케미칼":   "011170.KS",
    "한국전력":     "015760.KS",
}

US_STOCKS = {
    "Apple":        "AAPL",
    "Microsoft":    "MSFT",
    "NVIDIA":       "NVDA",
    "Amazon":       "AMZN",
    "Alphabet":     "GOOGL",
    "Meta":         "META",
    "Tesla":        "TSLA",
    "Berkshire":    "BRK-B",
    "JPMorgan":     "JPM",
    "Visa":         "V",
    "Johnson&Johnson":"JNJ",
    "Exxon":        "XOM",
    "UnitedHealth": "UNH",
    "Broadcom":     "AVGO",
    "Walmart":      "WMT",
}

INDICES = {
    "KOSPI":    "^KS11",
    "KOSDAQ":   "^KQ11",
    "S&P 500":  "^GSPC",
    "NASDAQ":   "^IXIC",
    "다우존스":  "^DJI",
}

ALL_STOCKS = {**KR_STOCKS, **US_STOCKS}
ALL_LABELS  = {v: k for k, v in ALL_STOCKS.items()}

PERIOD_MAP = {
    "1개월":  ("1mo",  "1d"),
    "3개월":  ("3mo",  "1d"),
    "6개월":  ("6mo",  "1d"),
    "1년":    ("1y",   "1wk"),
    "2년":    ("2y",   "1wk"),
    "5년":    ("5y",   "1mo"),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_info(ticker: str) -> dict:
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}

def fmt_pct(val):
    sign = "▲" if val >= 0 else "▼"
    cls  = "metric-delta-pos" if val >= 0 else "metric-delta-neg"
    return f'<span class="{cls}">{sign} {abs(val):.2f}%</span>'

def calc_return(df: pd.DataFrame) -> float | None:
    if df.empty or len(df) < 2:
        return None
    try:
        close = df["Close"].dropna()
        return float((close.iloc[-1] / close.iloc[0] - 1) * 100)
    except Exception:
        return None

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.6)",
    font=dict(family="Space Mono, Noto Sans KR", color="#8892a4", size=11),
    xaxis=dict(gridcolor="#1f2d45", zerolinecolor="#1f2d45"),
    yaxis=dict(gridcolor="#1f2d45", zerolinecolor="#1f2d45"),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1f2d45", borderwidth=1),
)

COLORS = ["#4d8cff","#00ff9d","#ffd166","#ff4d6d","#c77dff",
          "#06d6a0","#fb8500","#e63946","#118ab2","#ffd60a"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">⚙ 설정</div>', unsafe_allow_html=True)

    period_label = st.selectbox("기간", list(PERIOD_MAP.keys()), index=3)
    period, interval = PERIOD_MAP[period_label]

    st.markdown('<div class="section-title">🇰🇷 한국 주식</div>', unsafe_allow_html=True)
    kr_selected = st.multiselect(
        "종목 선택",
        list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "NAVER"],
        key="kr",
    )

    st.markdown('<div class="section-title">🇺🇸 미국 주식</div>', unsafe_allow_html=True)
    us_selected = st.multiselect(
        "종목 선택",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Tesla"],
        key="us",
    )

    show_indices = st.toggle("지수 오버레이 표시", value=True)
    show_volume  = st.toggle("거래량 표시", value=False)
    chart_type   = st.radio("차트 유형", ["라인", "캔들스틱"], horizontal=True)

    st.markdown("---")
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Selected tickers ──────────────────────────────────────────────────────────
selected_kr = {n: KR_STOCKS[n] for n in kr_selected}
selected_us = {n: US_STOCKS[n] for n in us_selected}
selected_all = {**selected_kr, **selected_us}

if not selected_all:
    st.warning("좌측 사이드바에서 종목을 하나 이상 선택해주세요.")
    st.stop()

# ── Hero ──────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%Y.%m.%d  %H:%M")
st.markdown(f"""
<div class="hero">
  <div class="hero-badge">LIVE MARKET DATA</div>
  <p class="hero-title">📈 글로벌 주식 비교 대시보드</p>
  <p class="hero-sub">한국 · 미국 주요 종목 수익률 & 차트 한눈에 비교 &nbsp;|&nbsp; 업데이트: {now_str}</p>
</div>
""", unsafe_allow_html=True)

# ── Fetch all data ────────────────────────────────────────────────────────────
with st.spinner("시세 데이터 불러오는 중..."):
    data: dict[str, pd.DataFrame] = {}
    for name, ticker in selected_all.items():
        data[name] = fetch_history(ticker, period, interval)

    idx_data: dict[str, pd.DataFrame] = {}
    if show_indices:
        for iname, iticker in INDICES.items():
            idx_data[iname] = fetch_history(iticker, period, interval)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 수익률 비교", "📈 가격 차트", "🕯 개별 종목", "📋 데이터 테이블"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — Return Comparison
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    returns = {}
    for name, df in data.items():
        r = calc_return(df)
        if r is not None:
            returns[name] = r

    if not returns:
        st.error("수익률 데이터를 가져오지 못했습니다.")
    else:
        # ── KPI row ──────────────────────────────────────────────────────────
        best_name  = max(returns, key=returns.get)
        worst_name = min(returns, key=returns.get)
        avg_return = np.mean(list(returns.values()))
        pos_count  = sum(1 for v in returns.values() if v >= 0)

        c1, c2, c3, c4 = st.columns(4)
        kpis = [
            (c1, "최고 수익률", best_name,  returns[best_name]),
            (c2, "최저 수익률", worst_name, returns[worst_name]),
            (c3, "평균 수익률", f"{len(returns)}개 종목",  avg_return),
            (c4, "상승 종목 수", f"{pos_count}/{len(returns)}",  None),
        ]
        for col, title, sub, val in kpis:
            with col:
                delta_html = fmt_pct(val) if val is not None else ""
                col.markdown(f"""
                <div class="metric-card">
                  <div class="metric-title">{title}</div>
                  <div class="metric-value">{sub}</div>
                  {delta_html}
                </div>""", unsafe_allow_html=True)

        # ── Bar chart ────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">수익률 순위 ({})'.format(period_label) + '</div>', unsafe_allow_html=True)

        sorted_ret = dict(sorted(returns.items(), key=lambda x: x[1], reverse=True))
        bar_colors = ["#00ff9d" if v >= 0 else "#ff4d6d" for v in sorted_ret.values()]
        bar_text   = [f"{v:+.2f}%" for v in sorted_ret.values()]

        fig_bar = go.Figure(go.Bar(
            x=list(sorted_ret.keys()),
            y=list(sorted_ret.values()),
            marker_color=bar_colors,
            text=bar_text,
            textposition="outside",
            textfont=dict(family="Space Mono", size=10),
        ))
        fig_bar.add_hline(y=0, line_width=1, line_color="#1f2d45")
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            height=380,
            yaxis_title="수익률 (%)",
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # ── Scatter: return vs volatility ─────────────────────────────────────
        st.markdown('<div class="section-title">리스크-수익률 산점도</div>', unsafe_allow_html=True)

        scatter_x, scatter_y, scatter_labels, scatter_colors = [], [], [], []
        for i, (name, df) in enumerate(data.items()):
            if df.empty or name not in returns:
                continue
            try:
                close = df["Close"].dropna()
                daily_ret = close.pct_change().dropna()
                vol = float(daily_ret.std() * (252 ** 0.5) * 100)
                scatter_x.append(vol)
                scatter_y.append(returns[name])
                scatter_labels.append(name)
                scatter_colors.append(COLORS[i % len(COLORS)])
            except Exception:
                pass

        if scatter_x:
            fig_sc = go.Figure()
            fig_sc.add_hline(y=0, line_color="#1f2d45", line_width=1)
            for sx, sy, sl, sc in zip(scatter_x, scatter_y, scatter_labels, scatter_colors):
                fig_sc.add_trace(go.Scatter(
                    x=[sx], y=[sy], mode="markers+text",
                    marker=dict(size=14, color=sc, line=dict(width=1, color="#fff")),
                    text=[sl], textposition="top center",
                    textfont=dict(size=9, color=sc),
                    name=sl, showlegend=False,
                ))
            fig_sc.update_layout(
                **PLOTLY_LAYOUT,
                height=380,
                xaxis_title="연간 변동성 (%)",
                yaxis_title="수익률 (%)",
            )
            st.plotly_chart(fig_sc, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — Normalized Price Chart
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">정규화 가격 차트 (시작 = 100)</div>', unsafe_allow_html=True)

    rows = 2 if show_volume else 1
    specs = [[{"secondary_y": False}]] * rows
    fig_norm = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                             row_heights=[0.75, 0.25] if show_volume else [1],
                             specs=specs, vertical_spacing=0.04)

    for i, (name, df) in enumerate(data.items()):
        if df.empty:
            continue
        try:
            close = df["Close"].dropna()
            norm  = close / close.iloc[0] * 100
            color = COLORS[i % len(COLORS)]
            fig_norm.add_trace(go.Scatter(
                x=norm.index, y=norm.values,
                name=name, line=dict(color=color, width=1.8),
                hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>지수: %{{y:.1f}}<extra></extra>",
            ), row=1, col=1)
            if show_volume and "Volume" in df.columns:
                vol_series = df["Volume"].dropna()
                fig_norm.add_trace(go.Bar(
                    x=vol_series.index, y=vol_series.values,
                    name=f"{name} 거래량", marker_color=color,
                    opacity=0.4, showlegend=False,
                    hovertemplate=f"<b>{name}</b> 거래량: %{{y:,.0f}}<extra></extra>",
                ), row=2, col=1)
        except Exception:
            pass

    # Overlay indices
    if show_indices:
        for iname, idf in idx_data.items():
            if idf.empty:
                continue
            try:
                close = idf["Close"].dropna()
                norm  = close / close.iloc[0] * 100
                fig_norm.add_trace(go.Scatter(
                    x=norm.index, y=norm.values,
                    name=iname, line=dict(color="#ffffff", width=1, dash="dot"),
                    opacity=0.4,
                    hovertemplate=f"<b>{iname}</b><br>%{{x|%Y-%m-%d}}<br>지수: %{{y:.1f}}<extra></extra>",
                ), row=1, col=1)
            except Exception:
                pass

    fig_norm.add_hline(y=100, line_color="#1f2d45", line_width=1, row=1, col=1)
    fig_norm.update_layout(**PLOTLY_LAYOUT, height=520, hovermode="x unified")
    fig_norm.update_xaxes(gridcolor="#1f2d45")
    fig_norm.update_yaxes(gridcolor="#1f2d45")
    st.plotly_chart(fig_norm, use_container_width=True)

    # ── Correlation heatmap ──────────────────────────────────────────────────
    st.markdown('<div class="section-title">종목 간 상관관계 히트맵</div>', unsafe_allow_html=True)

    corr_df = pd.DataFrame()
    for name, df in data.items():
        if not df.empty:
            try:
                close = df["Close"].dropna()
                corr_df[name] = close.pct_change()
            except Exception:
                pass

    if len(corr_df.columns) >= 2:
        corr_matrix = corr_df.corr()
        fig_heat = go.Figure(go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns.tolist(),
            y=corr_matrix.columns.tolist(),
            colorscale=[[0, "#ff4d6d"], [0.5, "#1a2236"], [1, "#00ff9d"]],
            zmin=-1, zmax=1,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            textfont=dict(size=10, family="Space Mono"),
            hoverongaps=False,
        ))
        fig_heat.update_layout(**PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig_heat, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — Individual Stock Candlestick
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">개별 종목 상세 분석</div>', unsafe_allow_html=True)

    stock_choice = st.selectbox("종목 선택", list(selected_all.keys()))
    ticker_choice = selected_all[stock_choice]
    df_ind = data[stock_choice]

    if df_ind.empty:
        st.error("데이터를 불러오지 못했습니다.")
    else:
        # Info panel
        info = fetch_info(ticker_choice)
        col_i1, col_i2, col_i3, col_i4 = st.columns(4)

        def info_card(col, title, value):
            col.markdown(f"""
            <div class="metric-card">
              <div class="metric-title">{title}</div>
              <div class="metric-value" style="font-size:16px">{value}</div>
            </div>""", unsafe_allow_html=True)

        market_cap = info.get("marketCap", 0)
        if market_cap:
            cap_str = f"${market_cap/1e12:.2f}T" if market_cap > 1e12 else f"${market_cap/1e9:.1f}B"
        else:
            cap_str = "N/A"

        info_card(col_i1, "52W 최고", f"{info.get('fiftyTwoWeekHigh','N/A')}")
        info_card(col_i2, "52W 최저", f"{info.get('fiftyTwoWeekLow','N/A')}")
        info_card(col_i3, "시가총액", cap_str)
        info_card(col_i4, "P/E Ratio", f"{info.get('trailingPE','N/A')}")

        # Candlestick / Line
        rows_ind = 2 if show_volume else 1
        fig_ind = make_subplots(
            rows=rows_ind, cols=1, shared_xaxes=True,
            row_heights=[0.75, 0.25] if show_volume else [1],
            vertical_spacing=0.04,
        )

        if chart_type == "캔들스틱" and all(c in df_ind.columns for c in ["Open","High","Low","Close"]):
            fig_ind.add_trace(go.Candlestick(
                x=df_ind.index,
                open=df_ind["Open"], high=df_ind["High"],
                low=df_ind["Low"],   close=df_ind["Close"],
                name=stock_choice,
                increasing_line_color="#00ff9d", decreasing_line_color="#ff4d6d",
                increasing_fillcolor="#00ff9d",  decreasing_fillcolor="#ff4d6d",
            ), row=1, col=1)
        else:
            close_s = df_ind["Close"].dropna()
            fig_ind.add_trace(go.Scatter(
                x=close_s.index, y=close_s.values,
                name=stock_choice, line=dict(color="#4d8cff", width=2),
                fill="tozeroy", fillcolor="rgba(77,140,255,0.07)",
            ), row=1, col=1)

        # Moving averages
        close_s = df_ind["Close"].dropna()
        for window, color, dash in [(20, "#ffd166", "solid"), (60, "#c77dff", "dot")]:
            if len(close_s) >= window:
                ma = close_s.rolling(window).mean()
                fig_ind.add_trace(go.Scatter(
                    x=ma.index, y=ma.values,
                    name=f"MA{window}", line=dict(color=color, width=1.2, dash=dash),
                ), row=1, col=1)

        if show_volume and "Volume" in df_ind.columns:
            vol_s = df_ind["Volume"].dropna()
            fig_ind.add_trace(go.Bar(
                x=vol_s.index, y=vol_s.values,
                name="거래량", marker_color="#4d8cff", opacity=0.5, showlegend=False,
            ), row=2, col=1)

        fig_ind.update_layout(**PLOTLY_LAYOUT, height=520, hovermode="x unified")
        fig_ind.update_xaxes(gridcolor="#1f2d45", rangeslider_visible=False)
        fig_ind.update_yaxes(gridcolor="#1f2d45")
        st.plotly_chart(fig_ind, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — Data Table
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">종목 요약 데이터</div>', unsafe_allow_html=True)

    rows_list = []
    for name, df in data.items():
        if df.empty:
            continue
        try:
            close = df["Close"].dropna()
            ret   = calc_return(df)
            info  = fetch_info(selected_all[name])
            daily_ret = close.pct_change().dropna()
            vol   = float(daily_ret.std() * (252 ** 0.5) * 100) if len(daily_ret) > 1 else None
            rows_list.append({
                "종목명": name,
                "티커": selected_all[name],
                "시장": "🇰🇷 KR" if selected_all[name].endswith(".KS") or selected_all[name].endswith(".KQ") else "🇺🇸 US",
                "현재가": f"{float(close.iloc[-1]):,.2f}",
                f"수익률({period_label})": f"{ret:+.2f}%" if ret is not None else "N/A",
                "연간변동성": f"{vol:.1f}%" if vol else "N/A",
                "52W 최고": info.get("fiftyTwoWeekHigh", "N/A"),
                "52W 최저": info.get("fiftyTwoWeekLow", "N/A"),
            })
        except Exception:
            pass

    if rows_list:
        table_df = pd.DataFrame(rows_list)
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        csv = table_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 CSV 다운로드", csv, "stock_data.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#2d3a52;font-size:11px;
            font-family:'Space Mono',monospace;margin-top:40px;padding:20px 0;">
  데이터 출처: Yahoo Finance (yfinance) &nbsp;|&nbsp; 본 정보는 투자 권유가 아닙니다
</div>
""", unsafe_allow_html=True)
