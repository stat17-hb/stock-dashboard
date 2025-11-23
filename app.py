import streamlit as st
import pandas as pd
from datetime import datetime
from modules.pension import PensionRebalancing
from modules.history import TransactionHistory

# 페이지 설정
st.set_page_config(
    page_title="STOCK DASHBOARD",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 주입
st.markdown("""
    <style>
        /* Global Settings */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        /* Apply Sans-Serif font to most text, but exclude icons */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: #D1D4DC;
        }
        
        /* Main Background */
        .stApp {
            background-color: #131722;
            color: #D1D4DC;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1E222D;
            border-right: 1px solid #2A2E39;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #D1D4DC !important;
            background-color: transparent;
            padding: 0;
            border: none;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        /* Text Colors */
        p, div, span, label {
            color: #D1D4DC;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #D1D4DC !important;
            font-size: 28px !important;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            color: #787B86 !important;
            font-size: 14px !important;
            font-weight: 400;
        }
        
        /* Dataframes */
        [data-testid="stDataFrame"] {
            background-color: #131722;
        }
        [data-testid="stDataFrame"] th {
            background-color: #1E222D !important;
            color: #D1D4DC !important;
            border-bottom: 1px solid #2A2E39 !important;
        }
        [data-testid="stDataFrame"] td {
            background-color: #131722 !important;
            color: #D1D4DC !important;
            border-bottom: 1px solid #2A2E39 !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            background-color: transparent;
            border-bottom: 1px solid #2A2E39;
            padding-bottom: 0;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: transparent;
            border: none;
            color: #787B86;
            font-weight: 600;
            padding: 0 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent !important;
            color: #2962FF !important;
            border-bottom: 2px solid #2962FF;
        }
        .stTabs [aria-selected="true"] p {
            color: #2962FF !important;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #2962FF;
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 600;
            transition: background-color 0.2s;
        }
        .stButton > button:hover {
            background-color: #1E53E5;
            color: #FFFFFF;
            border: none;
        }
        
        /* Inputs */
        .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > div {
            background-color: #1E222D;
            color: #D1D4DC;
            border: 1px solid #2A2E39;
            border-radius: 4px;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #1E222D !important;
            color: #D1D4DC !important;
            border: 1px solid #2A2E39;
            border-radius: 4px;
        }
        
        /* Divider */
        hr {
            border-color: #2A2E39;
            margin: 20px 0;
        }
        
        /* Ticker Row Styling */
        .ticker-row {
            display: flex; 
            justify-content: space-between; 
            background-color: #1E222D; 
            padding: 12px 20px; 
            border-bottom: 1px solid #2A2E39; 
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .ticker-item {
            color: #D1D4DC; 
            font-weight: 600; 
            font-size: 14px;
        }
        .ticker-up { color: #26a69a; }
        .ticker-down { color: #ef5350; }
        
    </style>
""", unsafe_allow_html=True)

# Ticker Row (Mock Data for Speed, or use simple fdr calls if preferred)
# Using static placeholders for now to ensure layout, can be connected to real data later
st.markdown("""
    <div class="ticker-row">
        <span class="ticker-item">S&P 500 <span class="ticker-up">▲ 5,088.80 (+1.03%)</span></span>
        <span class="ticker-item">NASDAQ <span class="ticker-up">▲ 16,041.62 (+1.30%)</span></span>
        <span class="ticker-item">KOSPI <span class="ticker-down">▼ 2,647.00 (-0.50%)</span></span>
        <span class="ticker-item">USD/KRW <span class="ticker-up">▲ 1,330.00 (+0.15%)</span></span>
        <span class="ticker-item">GOLD <span class="ticker-up">▲ 2,035.00 (+0.50%)</span></span>
    </div>
""", unsafe_allow_html=True)

# 타이틀
st.title("STOCK DASHBOARD")
st.markdown(f"**SYSTEM TIME**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 사이드바
with st.sidebar:
    st.header("SETTINGS")
    auto_refresh = st.checkbox("AUTO REFRESH (60s)", value=False)

    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()

    st.markdown("---")
    st.info("MONITORING ACTIVE")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["BY ACCOUNT", "ALL TRANSACTIONS", "PENSION REBALANCING"])

# 데이터 로드 (한 번만 로드하여 공유)
try:
    history = TransactionHistory()
    df_history = history.get_history()
except Exception as e:
    st.error(f"DATA FETCH ERROR: {e}")
    df_history = pd.DataFrame()

# 1. 계좌별 보기 탭
with tab1:
    st.header("Transaction History by Account")
    
    if not df_history.empty:
        accounts, account_col = history.get_accounts(df_history)
        
        if accounts:
            selected_account = st.selectbox("SELECT ACCOUNT", accounts)
            
            if selected_account:
                filtered_df = df_history[df_history[account_col] == selected_account]
                styled_df = history.style_dataframe(filtered_df)
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                st.caption(f"Records: {len(filtered_df)}")
        else:
            st.warning("ACCOUNT COLUMN NOT FOUND IN DATA")
            # 계좌 컬럼을 못 찾으면 전체 데이터 표시
            styled_df = history.style_dataframe(df_history)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.warning("NO DATA AVAILABLE")

# 2. 전체 보기 탭
with tab2:
    st.header("All Transactions")
    
    if not df_history.empty:
        styled_df = history.style_dataframe(df_history)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        st.caption(f"Total Records: {len(df_history)}")
    else:
        st.warning("NO DATA AVAILABLE")

# 3. 연금 리밸런싱 탭
with tab3:
    try:
        pension = PensionRebalancing()
        pension.display_dashboard()
    except Exception as e:
        st.error(f"DATA FETCH ERROR: {e}")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #787B86; font-family: Inter, sans-serif;'>
        <small>STOCK DASHBOARD | SYSTEM ONLINE</small>
    </div>
    """,
    unsafe_allow_html=True
)
