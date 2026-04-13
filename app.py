import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import IsolationForest
from scipy.stats import norm

# Page Config
st.set_page_config(page_title="Premium Analysis | Financial Intelligence", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for a Clean, Minimalist & Luxurious Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;1,500&display=swap');
    
    :root {
        --bg-dark: #07090F;
        --card-bg: rgba(15, 20, 31, 0.6);
        --border-color: rgba(212, 175, 55, 0.2);
        --accent-gold: #D4AF37;
        --text-main: #F8FAFC;
        --text-muted: #94A3B8;
        --positive: #10B981;
        --negative: #EF4444;
    }

    .stApp {
        background: linear-gradient(135deg, #0f141f 0%, #07090f 100%);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 500 !important;
        color: var(--accent-gold) !important;
        letter-spacing: 0.5px;
    }

    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(212, 175, 55, 0.5);
    }

    .metric-label {
        color: var(--text-muted);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        color: #FFFFFF;
        font-size: 1.75rem;
        font-weight: 400;
        letter-spacing: -0.5px;
    }

    .metric-delta {
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }

    #MainMenu, footer, header {visibility: hidden;}
    
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        font-family: 'Playfair Display', serif;
        font-size: 1.1rem;
        color: var(--text-muted);
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-gold) !important;
        border-bottom-color: var(--accent-gold) !important;
    }

    /* Table Styling for Insiders */
    .styled-table { border-collapse: collapse; width: 100%; color: var(--text-main); font-size: 0.9rem; }
    .styled-table th { color: var(--accent-gold); text-align: left; padding: 12px; border-bottom: 1px solid var(--border-color); }
    .styled-table td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
</style>
""", unsafe_allow_html=True)

def metric_card(label, value, delta=None, delta_color="normal"):
    color = "var(--text-muted)"
    if delta_color == "normal": color = "var(--positive)"
    elif delta_color == "inverse": color = "var(--negative)"
    elif delta_color == "warning": color = "var(--accent-gold)"
    
    delta_html = f'<div class="metric-delta" style="color: {color}">{delta}</div>' if delta else ""
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div>{delta_html}</div>', unsafe_allow_html=True)

st.markdown("### Financial Intelligence Dashboard")

col1, col2 = st.columns(2)
with col1:
    ticker_symbol = st.text_input("Enter Stock Ticker", value="NVDA").upper()
with col2:
    period = st.selectbox("Price Period", options=["1y", "2y", "5y", "max"], index=0)

if ticker_symbol:
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        info = ticker.info

        st.markdown("---")
        
        # Data Preparation
        qtr_financials = ticker.quarterly_financials
        qtr_cashflow = ticker.quarterly_cashflow
        qtr_financials_t = qtr_financials.transpose()
        
        # Header Section
        col_h1, col_h2 = st.columns([2, 1])
        with col_h1:
            st.title(f"{info.get('shortName', ticker_symbol)}")
            st.caption(f"{info.get('sector', 'N/A')} | {info.get('industry', 'N/A')} | {info.get('exchange', 'N/A')}")
        
        with col_h2:
            st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
            current_price = info.get('currentPrice', hist['Close'].iloc[-1] if not hist.empty else 0)
            prev_close = info.get('previousClose', current_price)
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0
            color = "#10B981" if change >= 0 else "#EF4444"
            st.markdown(f'<div style="font-size: 2.5rem; font-weight: 300; color: #FFFFFF;">${current_price:,.2f}</div><div style="font-size: 1.1rem; color: {color};">{"▲" if change >= 0 else "▼"} {abs(change):.2f} ({change_pct:+.2f}%)</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Tab Interface
        tab1, tab2, tab3 = st.tabs(["Overview & Fundamentals", "Market Sentiment & Signals", "Quantitative Research"])

        # ==========================================
        # TAB 1: OVERVIEW & FUNDAMENTALS
        # ==========================================
        with tab1:
            # Piotroski F-Score Calculation (Simplified)
            f_score = 0
            try:
                if not qtr_financials.empty:
                    net_inc = qtr_financials.loc['Net Income'].iloc[0]
                    prev_net_inc = qtr_financials.loc['Net Income'].iloc[1]
                    roa = net_inc / info.get('totalAssets', 1)
                    cfo = qtr_cashflow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in qtr_cashflow.index else 0
                    
                    if net_inc > 0: f_score += 1
                    if roa > 0: f_score += 1
                    if cfo > 0: f_score += 1
                    if cfo > net_inc: f_score += 1
                    if net_inc > prev_net_inc: f_score += 1
            except: pass

            st.markdown("<br>", unsafe_allow_html=True)
            p1, p2, p3, p4 = st.columns(4)
            with p1: metric_card("Avg Target", f"${info.get('targetMeanPrice', 'N/A')}")
            with p2: metric_card("F-Score (Health)", f"{f_score}/9", "Piotroski Quality Rank", "warning")
            with p3: metric_card("Return on Equity", f"{info.get('returnOnEquity', 0)*100:.2f}%")
            with p4: metric_card("Debt / Mkt Cap", f"{(info.get('totalDebt', 0)/info.get('marketCap', 1))*100:.2f}%")

            st.markdown("<br>", unsafe_allow_html=True)
            fig_price = go.Figure()
            fig_price.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="Price", increasing_line_color='#10B981', decreasing_line_color='#EF4444'))
            fig_price.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, height=500, font=dict(family="Inter", color="#94A3B8"))
            st.plotly_chart(fig_price, use_container_width=True)

        # ==========================================
        # TAB 2: MARKET SENTIMENT & SIGNALS
        # ==========================================
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            s1, s2 = st.columns([1, 2])
            
            with s1:
                st.markdown("### Signal Engine")
                # RSI Calculation
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1]
                
                # Bollinger Bands
                ma20 = hist['Close'].rolling(window=20).mean()
                std20 = hist['Close'].rolling(window=20).std()
                upper_bb = ma20 + (std20 * 2)
                lower_bb = ma20 - (std20 * 2)
                
                curr_bb_upper = upper_bb.iloc[-1]
                curr_bb_lower = lower_bb.iloc[-1]

                signal = "NEUTRAL"
                sig_color = "var(--text-muted)"
                if rsi < 35 and current_price <= curr_bb_lower:
                    signal = "BULLISH ENTRY"
                    sig_color = "var(--positive)"
                elif rsi > 65 and current_price >= curr_bb_upper:
                    signal = "BEARISH EXIT"
                    sig_color = "var(--negative)"

                metric_card("Momentum (RSI)", f"{rsi:.1f}", f"Signal: {signal}", "normal" if signal == "BULLISH ENTRY" else "inverse" if signal == "BEARISH EXIT" else "warning")
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("### Major Holders")
                inst = ticker.institutional_holders
                if inst is not None and not inst.empty:
                    st.dataframe(inst[['Holder', 'Shares', '% Out']], hide_index=True)
                else: st.info("Institutional data unavailable.")

            with s2:
                st.markdown("### Insider Transactions")
                insiders = ticker.insider_transactions
                if insiders is not None and not insiders.empty:
                    st.dataframe(insiders[['Date', 'Insider', 'Transaction', 'Shares']].head(10), hide_index=True)
                else: st.info("No recent insider transactions reported.")

        # ==========================================
        # TAB 3: QUANTITATIVE RESEARCH
        # ==========================================
        with tab3:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Correlation Matrix
            st.markdown("### Macro Asset Correlation (1Y)")
            try:
                corr_assets = [ticker_symbol, "SPY", "GLD", "USO", "^TNX"]
                corr_data = yf.download(corr_assets, period="1y")['Close'].pct_change().corr()
                fig_corr = px.imshow(corr_data, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
                fig_corr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94A3B8"))
                st.plotly_chart(fig_corr, use_container_width=True)
            except: st.warning("Correlation data currently unavailable.")

            st.markdown("---")
            
            # Original Outlier Detection
            if len(hist) > 50:
                df_out = hist.copy()
                df_out['Returns'] = df_out['Close'].pct_change()
                df_out['Vol_Change'] = df_out['Volume'].pct_change()
                df_out.dropna(inplace=True)
                iso = IsolationForest(contamination=0.03, random_state=42).fit_predict(df_out[['Returns', 'Vol_Change']])
                df_out['Anomaly'] = iso
                anoms = df_out[df_out['Anomaly'] == -1]
                
                fig_anom = go.Figure()
                fig_anom.add_trace(go.Scatter(x=df_out.index, y=df_out['Close'], mode='lines', line=dict(color='#94A3B8')))
                fig_anom.add_trace(go.Scatter(x=anoms.index, y=anoms['Close'], mode='markers', marker=dict(color='#D4AF37', size=8)))
                fig_anom.update_layout(title="Institutional Action Anomalies", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
                st.plotly_chart(fig_anom, use_container_width=True)

            # Original Bayesian Target
            st.markdown("### Bayesian Target Probability")
            if info.get('targetMeanPrice'):
                log_r = np.log(hist['Close']/hist['Close'].shift(1)).dropna()
                vol = log_r.std() * np.sqrt(252)
                drift = (log_r.mean() - 0.5 * vol**2) * 252
                dist = (np.log(info['targetMeanPrice']/current_price) - drift) / vol
                prob = (1 - norm.cdf(dist)) * 100
                metric_card("12M Success Probability", f"{prob:.1f}%", f"Target: ${info['targetMeanPrice']}", "warning")

    except Exception as e:
        st.error(f"Analysis Interrupted: {e}")