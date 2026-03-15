import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#streamlit run app.py


# Page Config
st.set_page_config(page_title="Rizal Finance | Premium Analysis", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Luxury Look
st.markdown("""
<style>
    #@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Montserrat:wght@700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Playfair+Display:ital,wght@0,600;1,600&display=swap');
    
    :root {
        --bg-color: #0B0F19;
        --card-bg: rgba(255, 255, 255, 0.05);
        --accent-color: #d4af37;
        --text-main: #E2E8F0;
        --text-dim: #A0A0A0;
    }

    .stApp {
        #background-color: var(--bg-color);
        background: radial-gradient(circle at top left, #141c2f 0%, #0b0f19 50%, #05080e 100%);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    #h1, h2, 
    h1 {
        color: #d4af37 !important;
        font-weight: 400 !important;
        letter-spacing: 1px;
        #text-transform: uppercase;
        font-size: 2.8rem !important;
        margin-top: 2rem !important;
    }
    
    h3 {
        color: #d4af37 !important;
        font-weight: 400 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 1.5rem !important;
        margin-top: 2rem !important;
    }

    /* Glassmorphism Card Style */
    .metric-card {
        #background: var(--card-bg);
        #border: 1px solid rgba(255, 255, 255, 0.05);
        #border-radius: 12px;
        #padding: 20px;
        #backdrop-filter: blur(10px);
        #transition: transform 0.3s ease, border-color 0.3s ease;
        #text-align: left;
        #margin-bottom: 20px;
        
        background: rgba(20, 28, 47, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.4s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(212, 175, 55, 0.5);
        box-shadow: 0 12px 40px 0 rgba(212, 175, 55, 0.15);
    }

    .metric-label {
        color: var(--text-dim);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #FFFFFF;
        font-size: 1.8rem ; #1.5rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }

    .metric-delta {
        font-size: 0.85rem;
        margin-top: 4px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(255,255,255,0.02);
    }

    /* Hide Streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 600;
        background: linear-gradient(45deg, #d4af37, #f3e5ab, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 0px 4px 20px rgba(212, 175, 55, 0.2);
    }
    
    .sub-title {
        color: #94A3B8; 
        font-size: 1.1rem; 
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }

    /* Top Title Style */
    .lux-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 600;
        background: linear-gradient(45deg, #d4af37, #f3e5ab, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 0px 4px 20px rgba(212, 175, 55, 0.2);
    }
    
    .lux-subtitle {
        color: #94A3B8; 
        font-size: 1.1rem; 
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

def metric_card(label, value, delta=None, delta_color="normal"):
    delta_html = ""
    if delta:
        color = "#00FF41" if delta_color == "normal" else "#FF3131"
        delta_html = f'<div class="metric-delta" style="color: {color}">{delta}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

#st.title(":grey[Financial Intelligence Dashboard]")
st.markdown("### Financial Intelligence Dashboard")
#st.markdown("###")
#st.markdown('<p class="main-title">Financial Intelligence Dashboard</p>', unsafe_allow_html=True)
#st.markdown('<p class="sub-title">Premium Financial Analysis & Insights</p>', unsafe_allow_html=True)

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
        
        # Header Section
        col_header_1, col_header_2 = st.columns([2, 1])
        with col_header_1:
            st.title(f"{info['shortName']}")
            st.caption(f"{info.get('sector', '')} | {info['industry']} | {info.get('exchange', '')}")
        
        with col_header_2:
            st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
            current_price = info.get('currentPrice', 0)
            prev_close = info.get('previousClose', current_price)
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0
            color = "#00FF41" if change >= 0 else "#FF3131"
            arrow = "▲" if change >= 0 else "▼"

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

        #st.markdown("### Selection & Controls")
        #col_input_1, col_input_2, col_input_3 = st.columns([1, 1, 2])
        #with col_input_1:
        #    ticker_symbol = st.text_input("Ticker", value=ticker_symbol).upper()
        #with col_input_2:
        #    period = st.selectbox("Timeline", options=["1y", "2y", "5y", "max"], index=1)


        
        st.markdown("### Price Performance")
        potential_chg = info.get('targetMeanPrice', 'N/A') - current_price
        potential_chg_perc = (potential_chg/current_price)*100
        
        
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            metric_card("Day Range",f"${info.get('regularMarketDayRange','N/A')}")
        with p2:
            metric_card("52W Range", f"${info.get('fiftyTwoWeekRange', 'N/A')}")
        with p3:
            metric_card("Avg Target", f"${info.get('targetMeanPrice', 'N/A')}")
        with p4:
            if potential_chg_perc > 0:
                metric_card("Upside %", f"{round(potential_chg_perc,1)}%")
            else:
                metric_card("Upside %", f"N/A")
                

        
        
        st.markdown("### Key Metrics")
        
        # Calculations for Ratios
        market_cap = info.get('marketCap', 1)
        total_debt = info.get('totalDebt', 0)
        debt_to_mcap = (total_debt / market_cap) if market_cap else 0
            
        # Interest Income Ratio
        qtr_financials_transposed = ticker.quarterly_financials.transpose()
        if 'Interest Income' in qtr_financials_transposed.columns:
            qtr_interest_income = qtr_financials_transposed['Interest Income'].iloc[0]
        elif 'Net Interest Income' in qtr_financials_transposed.columns:
            qtr_interest_income = qtr_financials_transposed['Net Interest Income'].iloc[0]
        else:
            qtr_interest_income = 0

        qtr_total_revenue = qtr_financials_transposed['Total Revenue'].iloc[0] if 'Total Revenue' in qtr_financials_transposed.columns else 1
        qtr_interest_income_ratio = (qtr_interest_income / qtr_total_revenue) if qtr_total_revenue else 0


        forwardPE = info.get('forwardPE', 'N/A')
        trailingPE = info.get('trailingPE', 'N/A')
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_card("Debt / Mkt Cap", f"{debt_to_mcap*100:.2f}%")
        with m2:
            metric_card("Int. Inc / Rev", f"{qtr_interest_income_ratio*100:.2f}%")
        with m3:
            metric_card("Forward P/E", f"{forwardPE:.2f}")
        with m4:
            metric_card("Trailing P/E", f"{trailingPE}")
        
        st.markdown("#####")
        returnOnEquity = info.get('returnOnEquity')
        returnOnEquity = round(returnOnEquity*100,2) if isinstance(returnOnEquity, float) else 'N/A'

        #ebitdaMargins = info.get('ebitdaMargins')
        r1,r2,r3,r4 = st.columns(4)
        with r1:
            metric_card("Return On Equity",f"{returnOnEquity}%")
        with r2:
            metric_card("Ebitda Margins",f"{info.get('ebitdaMargins','N/A')}")
        with r3:
            metric_card("Quick Ratio",f"{info.get('quickRatio','N/A')}")
        with r4:
            metric_card("Beta",f"{info.get('beta','N/A')}")


        #st.markdown('#')
        st.markdown(f"### Technical Analysis: {ticker_symbol}")
        fig_price = go.Figure()
        # Candlestick
        fig_price.add_trace(go.Candlestick(
            x=hist.index, open=hist['Open'], high=hist['High'],
            low=hist['Low'], close=hist['Close'], name="Market Data",
            increasing_line_color='#00FF41', decreasing_line_color='#FF3131'
        ))
        # 1. Technical Indicators (EMAs)
        for span in [10, 20, 50, 150, 200]:
            hist[f'EMA{span}'] = hist['Close'].ewm(span=span, adjust=False).mean()
            
        # EMAs
        colors = {10: '#00D1FF', 20: '#FFA500', 50: '#FF0000', 150: '#A020F0', 200: '#FFFFFF'}
        #colors = {10: '#d4af37', 20: '#C0C0C0', 50: '#CD7F32', 150: '#FFFFFF', 200: '#8A9A5B'}
        for span in [10, 20, 50, 150, 200]:
            fig_price.add_trace(go.Scatter(
                x=hist.index, y=hist[f'EMA{span}'],
                line=dict(width=1.5, color=colors[span]), 
                name=f'EMA {span}',
                opacity=0.8
            ))

        fig_price.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False, 
            height=600, 
            template="plotly_dark",
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(family="Inter", color="#E0E0E0")
        )
        fig_price.update_xaxes(showgrid=False, zeroline=False)
        fig_price.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
        
        st.plotly_chart(fig_price, use_container_width=True)


         





        #st.markdown('#')
        st.markdown(f"### Fundamental Performance: {ticker_symbol} ({info.get("financialCurrency","N/A")})")
        # Fetch Financial Statements
        q_financials = ticker.quarterly_financials
        q_cashflow = ticker.quarterly_cashflow

        # Extract specific rows
        revenue = q_financials.loc['Total Revenue'] if 'Total Revenue' in q_financials.index else pd.Series()
        net_income = q_financials.loc['Net Income'] if 'Net Income' in q_financials.index else pd.Series()
        capex = q_cashflow.loc['Capital Expenditure'] if 'Capital Expenditure' in q_cashflow.index else pd.Series()

        if 'Free Cash Flow' in q_cashflow.index:
            fcf = q_cashflow.loc['Free Cash Flow']
        else:
            fcf = (q_cashflow.loc['Operating Cash Flow'] + capex) if 'Operating Cash Flow' in q_cashflow.index else pd.Series()

        fundamentals_df = pd.DataFrame({
            'Revenue': revenue,
            'Net Income': net_income,
            'Free Cash Flow': fcf,
            'CAPEX': capex.abs()
        }).dropna(how='all').sort_index()

        if not fundamentals_df.empty:
            fig_fin = go.Figure()
            fin_colors = ['#00D1FF', '#00FF41', '#FFA500', '#FF3131']
            #fin_colors = ['#d4af37', '#C0C0C0', '#CD7F32', '#B8860B']
            for i, col in enumerate(fundamentals_df.columns):
                fig_fin.add_trace(go.Bar(
                    x=fundamentals_df.index, 
                    y=fundamentals_df[col], 
                    name=col,
                    marker_color=fin_colors[i],
                    opacity=0.9
                ))

            fig_fin.update_layout(
                barmode='group', 
                height=500, 
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=30, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                font=dict(family="Inter", color="#E0E0E0")
            )
            fig_fin.update_xaxes(showgrid=False)
            fig_fin.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
            st.plotly_chart(fig_fin, use_container_width=True)
        else:
            st.warning("Insufficient financial data available for charts.")

        with st.expander("Show Business Summary"):
            st.write(info.get('longBusinessSummary', 'No summary available.'))

        with st.expander("Raw API Data"):
            st.json(info)

        
        

    except Exception as e:
        st.error(f"Error fetching data for {ticker_symbol}: {e}")
        st.info("Ensure the ticker is correct (e.g., AAPL, TSLA, MSFT).")

