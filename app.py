import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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

    /* Premium Glassmorphism Cards */
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
        box-shadow: 0 10px 30px -5px rgba(212, 175, 55, 0.15);
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

    /* Clean up Streamlit UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style Streamlit Tabs to match Luxury Theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        color: var(--text-muted);
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-gold) !important;
        border-bottom-color: var(--accent-gold) !important;
    }
</style>
""", unsafe_allow_html=True)

def metric_card(label, value, delta=None, delta_color="normal"):
    delta_html = ""
    if delta:
        color = "var(--positive)" if delta_color == "normal" else "var(--negative)"
        if delta_color == "warning": color = "var(--accent-gold)"
        delta_html = f'<div class="metric-delta" style="color: {color}">{delta}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def calculate_rsi_signal(hist, current_price):
    # RSI Calculation
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_val = 100 - (100 / (1 + rs)).iloc[-1]
            
    # Bollinger Bands
    ma20 = hist['Close'].rolling(window=20).mean()
    std20 = hist['Close'].rolling(window=20).std()
    upper_bb = ma20 + (std20 * 2)
    lower_bb = ma20 - (std20 * 2)
    
    curr_bb_upper = upper_bb.iloc[-1]
    curr_bb_lower = lower_bb.iloc[-1]

    signal = "NEUTRAL"
    sig_color = "var(--text-muted)"
    if rsi_val < 35 and current_price <= curr_bb_lower:
        signal = "BULLISH ENTRY"
        sig_color = "var(--positive)"
    elif rsi_val > 65 and current_price >= curr_bb_upper:
        signal = "BEARISH EXIT"
        sig_color = "var(--negative)"

    return rsi_val, signal, sig_color


st.markdown("### Financial Intelligence Dashboard")

# Sidebar - User Input
col1, col2 = st.columns(2)
with col1:
    ticker_symbol = st.text_input("Enter Stock Ticker", value="NVDA").upper()
with col2:
    period = st.selectbox("Price Period", options=["1y", "2y", "5y", "max"], index=1)

if ticker_symbol:
    try:
        # Fetch Data
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        info = ticker.info

        st.markdown("---")
        
        # Additional Data for Ratios and Charts
        qtr_financials = ticker.quarterly_financials
        qtr_cashflow = ticker.quarterly_cashflow
        qtr_financials_transposed = qtr_financials.transpose()
        
        # Header Section & Price Metrics
        current_price = info.get('currentPrice', 0)
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0
        color = "#00FF41" if change >= 0 else "#FF3131"
        arrow = "▲" if change >= 0 else "▼"

        col_header_1, col_header_2, col_header_3 = st.columns([3, 1.5, 1.5])
        
        with col_header_1:
            st.title(f"{info.get('shortName', ticker_symbol)}")
            st.caption(f"{info.get('sector', 'N/A')} | {info.get('industry', 'N/A')} | {info.get('exchange', 'N/A')}")
        
        with col_header_2:
            st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
            
            pre_market_price = info.get('preMarketPrice')
            post_market_price = info.get('postMarketPrice')
            
            market_extras = ""
            if pre_market_price is not None:
                pre_change = pre_market_price - current_price
                pre_change_pct = (pre_change / current_price) * 100 if current_price else 0
                pre_color = "#00FF41" if pre_change >= 0 else "#FF3131"
                pre_arrow = "▲" if pre_change >= 0 else "▼"
                market_extras += f'<div style="font-size: 0.9rem; color: #A0A0A0; margin-top: 5px;">Pre-Market: ${pre_market_price:,.2f} <span style="color: {pre_color};">{pre_arrow} {abs(pre_change):.2f} ({pre_change_pct:+.2f}%)</span></div>'
            
            if post_market_price is not None:
                post_change = post_market_price - current_price
                post_change_pct = (post_change / current_price) * 100 if current_price else 0
                post_color = "#00FF41" if post_change >= 0 else "#FF3131"
                post_arrow = "▲" if post_change >= 0 else "▼"
                market_extras += f'<div style="font-size: 0.9rem; color: #A0A0A0; margin-top: 5px;">Post-Market: ${post_market_price:,.2f} <span style="color: {post_color};">{post_arrow} {abs(post_change):.2f} ({post_change_pct:+.2f}%)</span></div>'
            
            st.markdown(f"""
                <div style="font-size: 2.5rem; font-weight: 700; color: #FFFFFF;">${current_price:,.2f}</div>
                <div style="font-size: 1.1rem; color: {color};">{arrow} {abs(change):.2f} ({change_pct:+.2f}%)</div>
                {market_extras}
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_header_3:
            rsi_val, signal, sig_color = calculate_rsi_signal(hist, current_price)
            #metric_card("Momentum (RSI)", f"{rsi_val:.1f}", f"Signal: {signal}", "normal" if signal == "BULLISH ENTRY" else "inverse" if signal == "BEARISH EXIT" else "warning")
            st.metric(st.markdown("Momentum (RSI)"), f"{rsi_val:.1f}", f"Signal: {signal}", "normal" if signal == "BULLISH ENTRY" else "inverse" if signal == "BEARISH EXIT" else "warning")
            

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Calculations for Additional Metrics
        # 1. Interest Income Ratio
        if not qtr_financials_transposed.empty:
            if 'Interest Income' in qtr_financials_transposed.columns:
                qtr_interest_income = qtr_financials_transposed['Interest Income'].iloc[0]
            elif 'Net Interest Income' in qtr_financials_transposed.columns:
                qtr_interest_income = qtr_financials_transposed['Net Interest Income'].iloc[0]
            else:
                qtr_interest_income = 0

            qtr_total_revenue = qtr_financials_transposed['Total Revenue'].iloc[0] if 'Total Revenue' in qtr_financials_transposed.columns else 1
        else:
            qtr_interest_income = 0
            qtr_total_revenue = 1
            
        interest_income_ratio = (qtr_interest_income / qtr_total_revenue) * 100 if qtr_total_revenue else 0

        # 2. Efficiency Ratios
        roe = info.get('returnOnEquity')
        roe_val = f"{roe*100:.2f}%" if roe is not None else "N/A"
        
        ebitda_margin = info.get('ebitdaMargins')
        ebitda_margin_val = f"{ebitda_margin*100:.2f}%" if ebitda_margin is not None else "N/A"

        # 3. Liquidity
        quick_ratio = info.get('quickRatio', 'N/A')
        
        # 4. Debt & Market
        market_cap = info.get('marketCap', 1)
        total_debt = info.get('totalDebt', 0)
        debt_to_mcap = (total_debt / market_cap) * 100 if market_cap else 0

        # ---- TABS INTERFACE ----
        tab1, tab2 = st.tabs(["Overview & Fundamentals", "Advanced Analytics"])

        # ==========================================
        # TAB 1: STANDARD DASHBOARD
        # ==========================================
        with tab1:
            # Row 1: Price Performance
            potential_chg = info.get('targetMeanPrice', 0) - current_price if info.get('targetMeanPrice') else 0
            potential_chg_perc = (potential_chg / current_price) * 100 if current_price else 0
            
            p1, p2, p3, p4 = st.columns(4)
            with p1: metric_card("Day Range", f"${info.get('regularMarketDayRange', 'N/A')}")
            with p2: metric_card("52W Range", f"${info.get('fiftyTwoWeekRange', 'N/A')}")
            with p3: metric_card("Avg Target", f"${info.get('targetMeanPrice', 'N/A')}")
            with p4: metric_card("Upside", f"{round(potential_chg_perc, 1)}%" if potential_chg_perc else "N/A", delta_color="normal" if potential_chg_perc > 0 else "inverse")

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Row 2: Valuation & Debt
            m1, m2, m3, m4 = st.columns(4)
            with m1: metric_card("Debt / Mkt Cap", f"{debt_to_mcap:.2f}%")
            with m2: metric_card("Int. Income / Rev", f"{interest_income_ratio:.2f}%")
            with m3: metric_card("Forward P/E", f"{info.get('forwardPE', 'N/A')}")
            with m4: metric_card("Trailing P/E", f"{info.get('trailingPE', 'N/A')}")

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Row 3: Efficiency & Health
            r1, r2, r3, r4 = st.columns(4)
            with r1: metric_card("Return on Equity", roe_val)
            with r2: metric_card("EBITDA Margin", ebitda_margin_val)
            with r3: metric_card("Quick Ratio", f"{quick_ratio}")
            with r4: metric_card("Beta", f"{info.get('beta', 'N/A')}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"### Technical Analysis")
            
            fig_price = go.Figure()
            
            # Candlestick
            fig_price.add_trace(go.Candlestick(
                x=hist.index, open=hist['Open'], high=hist['High'],
                low=hist['Low'], close=hist['Close'], name="Price action",
                increasing_line_color='#10B981', decreasing_line_color='#EF4444'
            ))
            
            # EMAs
            colors = {10: '#E2E8F0', 20: '#D4AF37', 50: '#94A3B8', 150: '#475569', 200: '#334155'}
            for span in [10, 20, 50, 150, 200]:
                hist[f'EMA{span}'] = hist['Close'].ewm(span=span, adjust=False).mean()
                fig_price.add_trace(go.Scatter(
                    x=hist.index, y=hist[f'EMA{span}'],
                    line=dict(width=1.5, color=colors[span]), 
                    name=f'EMA {span}', opacity=0.85
                ))

            fig_price.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, 
                height=600, margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                font=dict(family="Inter", color="#94A3B8"), hovermode="x unified"
            )
            fig_price.update_xaxes(showgrid=False, zeroline=False)
            fig_price.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
            st.plotly_chart(fig_price, use_container_width=True)

            # --- Fundamental Performance Section ---
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"### Fundamental Performance ({info.get('financialCurrency', 'N/A')})")
            
            # Extract specific rows for historical fundamentals
            revenue = qtr_financials.loc['Total Revenue'] if 'Total Revenue' in qtr_financials.index else pd.Series()
            net_income = qtr_financials.loc['Net Income'] if 'Net Income' in qtr_financials.index else pd.Series()
            capex = qtr_cashflow.loc['Capital Expenditure'] if 'Capital Expenditure' in qtr_cashflow.index else pd.Series()

            if 'Free Cash Flow' in qtr_cashflow.index:
                fcf = qtr_cashflow.loc['Free Cash Flow']
            else:
                fcf = (qtr_cashflow.loc['Operating Cash Flow'] + capex) if 'Operating Cash Flow' in qtr_cashflow.index else pd.Series()

            fundamentals_df = pd.DataFrame({
                'Revenue': revenue,
                'Net Income': net_income,
                'Free Cash Flow': fcf,
                'CAPEX': capex.abs()
            }).dropna(how='all').sort_index()

            if not fundamentals_df.empty:
                fig_fin = go.Figure()
                # fin_colors: Revenue (Gold), Net Income (Green), FCF (Light Blue), CAPEX (Red)
                fin_colors = ['#D4AF37', '#10B981', '#38BDF8', '#EF4444']
                for i, col in enumerate(fundamentals_df.columns):
                    fig_fin.add_trace(go.Bar(
                        x=fundamentals_df.index, 
                        y=fundamentals_df[col], 
                        name=col,
                        marker_color=fin_colors[i],
                        opacity=0.9
                    ))

                fig_fin.update_layout(
                    barmode='group', height=500, template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=30, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    font=dict(family="Inter", color="#94A3B8")
                )
                fig_fin.update_xaxes(showgrid=False)
                fig_fin.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
                st.plotly_chart(fig_fin, use_container_width=True)
            else:
                st.warning("Insufficient quarterly financial data available for charts.")

            with st.expander("Business Summary"):
                st.write(info.get('longBusinessSummary', 'No summary available.'))


        # ==========================================
        # TAB 2: ADVANCED ANALYTICS
        # ==========================================
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 1. OUTLIER DETECTION (Isolation Forest)
            st.markdown("### Institutional Action Anomalies (Outlier Detection)")
            st.write("Identifies statistically anomalous trading days based on combined price action and volume divergence.")
            
            if len(hist) > 50:
                df_outlier = hist.copy()
                df_outlier['Returns'] = df_outlier['Close'].pct_change()
                df_outlier['Vol_Change'] = df_outlier['Volume'].pct_change()
                df_outlier.dropna(inplace=True)
                
                # Model
                features = df_outlier[['Returns', 'Vol_Change']]
                iso_forest = IsolationForest(contamination=0.03, random_state=42) # 3% of data flagged as anomalies
                df_outlier['Anomaly'] = iso_forest.fit_predict(features)
                anomalies = df_outlier[df_outlier['Anomaly'] == -1]

                fig_anom = go.Figure()
                fig_anom.add_trace(go.Scatter(x=df_outlier.index, y=df_outlier['Close'], mode='lines', name='Close Price', line=dict(color='#94A3B8', width=2)))
                fig_anom.add_trace(go.Scatter(
                    x=anomalies.index, y=anomalies['Close'], mode='markers', name='Anomalous Volume/Price Action',
                    marker=dict(color='#D4AF37', size=10, line=dict(color='white', width=1), symbol='circle-open-dot')
                ))
                fig_anom.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400,
                    margin=dict(l=0, r=0, t=10, b=0), font=dict(family="Inter", color="#94A3B8"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig_anom.update_xaxes(showgrid=False)
                fig_anom.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                st.plotly_chart(fig_anom, use_container_width=True)
            else:
                st.warning("Not enough data points for Outlier Detection.")

            st.markdown("---")

            # 2. BAYESIAN TARGET PROBABILITY MODELING
            st.markdown("### Bayesian Target Probability Modeling")
            target_price = info.get('targetMeanPrice', None)
            
            if target_price and current_price and len(hist) > 0:
                st.write(f"Calculating the statistical probability of reaching the mean target of **${target_price}** within 12 months, based on historical drift and volatility.")
                
                # Calculate daily log returns
                log_returns = np.log(hist['Close'] / hist['Close'].shift(1)).dropna()
                mu = log_returns.mean()
                sigma = log_returns.std()
                
                # Annualize (assuming 252 trading days)
                trading_days = 252
                drift = (mu - 0.5 * sigma**2) * trading_days
                volatility = sigma * np.sqrt(trading_days)
                
                # Probability calculation (Distance to target in standard deviations)
                # P(S_T > Target) = 1 - CDF((ln(Target/Current) - Drift) / Volatility)
                distance = (np.log(target_price / current_price) - drift) / volatility
                prob_hit_target = (1 - norm.cdf(distance)) * 100

                col_prob1, col_prob2 = st.columns(2)
                with col_prob1:
                    metric_card("Analyst Mean Target", f"${target_price}", f"Current: ${current_price:,.2f}", "warning")
                with col_prob2:
                    metric_card("12-Month Probability", f"{prob_hit_target:.1f}%", f"Historical Volatility: {volatility*100:.1f}%", "normal" if prob_hit_target > 50 else "inverse")
            else:
                st.info("Target price or historical data unavailable for this ticker.")

            st.markdown("---")

            # 3. RELATIVE STRENGTH (ALPHA)
            st.markdown("### Relative Strength vs. S&P 500 (Alpha Generation)")
            st.write("Compares the normalized cumulative return of the selected asset against the broad market benchmark (SPY).")
            
            try:
                spy = yf.Ticker("SPY").history(period=period)
                if not spy.empty and not hist.empty:
                    # Align dates and normalize to base 100
                    common_index = hist.index.intersection(spy.index)
                    asset_returns = hist.loc[common_index, 'Close'] / hist.loc[common_index, 'Close'].iloc[0] * 100
                    spy_returns = spy.loc[common_index, 'Close'] / spy.loc[common_index, 'Close'].iloc[0] * 100
                    
                    alpha_final = asset_returns.iloc[-1] - spy_returns.iloc[-1]

                    fig_rs = go.Figure()
                    fig_rs.add_trace(go.Scatter(x=common_index, y=asset_returns, mode='lines', name=ticker_symbol, line=dict(color='#D4AF37', width=2)))
                    fig_rs.add_trace(go.Scatter(x=common_index, y=spy_returns, mode='lines', name='SPY (Benchmark)', line=dict(color='#475569', width=2, dash='dot')))
                    
                    fig_rs.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400,
                        margin=dict(l=0, r=0, t=10, b=0), font=dict(family="Inter", color="#94A3B8"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        title=f"Cumulative Alpha: {alpha_final:+.2f}%"
                    )
                    fig_rs.update_xaxes(showgrid=False)
                    fig_rs.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                    st.plotly_chart(fig_rs, use_container_width=True)
            except Exception as e:
                st.warning("Could not load benchmark data for relative strength comparison.")

    except Exception as e:
        st.error(f"System Error: {e}")
        st.info("Ensure the ticker symbol is valid.")
