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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Montserrat:wght@700&display=swap');
    
    :root {
        --bg-color: #0E1117;
        --card-bg: rgba(255, 255, 255, 0.03);
        --accent-color: #00D1FF;
        --text-main: #E0E0E0;
        --text-dim: #A0A0A0;
    }

    .stApp {
        background-color: var(--bg-color);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* Glassmorphism Card Style */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, border-color 0.3s ease;
        text-align: left;
        margin-bottom: 20px;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        border-color: var(--accent-color);
        background: rgba(255, 255, 255, 0.05);
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
        font-size: 1.5rem;
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
        font-size: 3rem;
        background: linear-gradient(135deg, #FFFFFF 0%, #00D1FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: var(--text-dim);
        font-size: 1.1rem;
        font-weight: 300;
        margin-bottom: 30px;
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

#st.title(":green[Financial Intelligence Dashboard]")
st.title("Financial Intelligence Dashboard")
#st.markdown("###")
#st.markdown('<p class="main-title">Financial Intelligence Dashboard</p>', unsafe_allow_html=True)
#st.markdown('<p class="sub-title">Premium Financial Intelligence Dashboard</p>', unsafe_allow_html=True)

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
            
            st.markdown(f"""
                <div style="font-size: 2.5rem; font-weight: 700; color: #FFFFFF;">${current_price:,.2f}</div>
                <div style="font-size: 1.1rem; color: {color};">{arrow} {abs(change):.2f} ({change_pct:+.2f}%)</div>
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
        
        
        p1, p2, p3, p4, p5, p6 = st.columns(6)
        with p1:
            metric_card("Day Low", f"${info.get('dayLow', 'N/A')}")
        with p2:
            metric_card("Day High", f"${info.get('dayHigh', 'N/A')}")
        with p3:
            metric_card("52W Low", f"${info.get('fiftyTwoWeekLow', 'N/A')}")
        with p4:
            metric_card("52W High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")
        with p5:
            metric_card("Avg Target", f"${info.get('targetMeanPrice', 'N/A')}")
        with p6:
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

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_card("Debt / Mkt Cap", f"{debt_to_mcap*100:.2f}%")
        with m2:
            metric_card("Int. Inc / Rev", f"{qtr_interest_income_ratio*100:.2f}%")
        with m3:
            metric_card("Forward P/E", f"{info.get('forwardPE', 'N/A')}")
        with m4:
            metric_card("Trailing P/E", f"{info.get('trailingPE', 'N/A')}")
        
        
    
        


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
        st.markdown(f"### Fundamental Performance: {ticker_symbol}")
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
