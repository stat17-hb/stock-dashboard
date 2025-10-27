import streamlit as st
import pandas as pd
from datetime import datetime
from modules.korean_stocks import KoreanPortfolio
from modules.us_stocks import USPortfolio

# 페이지 설정
st.set_page_config(
    page_title="보유종목 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 타이틀
st.title("📊 보유종목 대시보드")
st.markdown(f"**조회 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 사이드바
with st.sidebar:
    st.header("설정")
    auto_refresh = st.checkbox("자동 새로고침 (60초)", value=False)

    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()

    st.markdown("---")
    st.info("국내주식과 해외주식 포트폴리오를 실시간으로 모니터링합니다.")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["국내 ETF", "해외 주식", "전체 요약"])

# 국내 ETF 탭
with tab1:
    st.header("🇰🇷 국내 ETF 포트폴리오")

    try:
        korean_portfolio = KoreanPortfolio()
        korean_portfolio.display_dashboard()
    except Exception as e:
        st.error(f"국내 ETF 데이터 조회 중 오류가 발생했습니다: {e}")

# 해외 주식 탭
with tab2:
    st.header("🇺🇸 해외 주식 포트폴리오")

    try:
        us_portfolio = USPortfolio()
        us_portfolio.display_dashboard()
    except Exception as e:
        st.error(f"해외 주식 데이터 조회 중 오류가 발생했습니다: {e}")

# 전체 요약 탭
with tab3:
    st.header("📈 전체 포트폴리오 요약")

    try:
        # 국내 ETF 데이터
        korean_portfolio = KoreanPortfolio()
        korean_summary = korean_portfolio.get_portfolio_summary()

        # 해외 주식 데이터
        us_portfolio = USPortfolio()
        us_summary = us_portfolio.get_portfolio_summary()

        # 전체 요약 메트릭
        col1, col2, col3 = st.columns(3)

        with col1:
            total_investment = korean_summary['total_investment'] + us_summary['total_investment_krw']
            st.metric(
                "총 투자금액",
                f"{total_investment:,.0f}원"
            )

        with col2:
            total_value = korean_summary['total_current_value'] + us_summary['total_current_value_krw']
            st.metric(
                "현재 총 자산",
                f"{total_value:,.0f}원"
            )

        with col3:
            total_profit = korean_summary['total_profit_loss'] + us_summary['total_profit_loss_krw']
            total_return = (total_profit / total_investment * 100) if total_investment > 0 else 0
            st.metric(
                "총 수익률",
                f"{total_return:+.2f}%",
                f"{total_profit:+,.0f}원"
            )

        st.markdown("---")

        # 포트폴리오 비율 차트
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("포트폴리오 구성 비율")
            portfolio_data = pd.DataFrame({
                '구분': ['국내 ETF', '해외 주식'],
                '금액': [korean_summary['total_current_value'], us_summary['total_current_value_krw']]
            })
            st.bar_chart(portfolio_data.set_index('구분'))

        with col2:
            st.subheader("수익률 비교")
            return_data = pd.DataFrame({
                '구분': ['국내 ETF', '해외 주식'],
                '수익률(%)': [korean_summary['total_return'], us_summary['total_return']]
            })
            st.bar_chart(return_data.set_index('구분'))

        # 상세 데이터 테이블
        st.markdown("---")
        st.subheader("상세 비교")

        comparison_df = pd.DataFrame({
            '구분': ['국내 ETF', '해외 주식', '합계'],
            '투자금액': [
                f"{korean_summary['total_investment']:,.0f}원",
                f"{us_summary['total_investment_krw']:,.0f}원",
                f"{total_investment:,.0f}원"
            ],
            '현재가치': [
                f"{korean_summary['total_current_value']:,.0f}원",
                f"{us_summary['total_current_value_krw']:,.0f}원",
                f"{total_value:,.0f}원"
            ],
            '수익률': [
                f"{korean_summary['total_return']:+.2f}%",
                f"{us_summary['total_return']:+.2f}%",
                f"{total_return:+.2f}%"
            ],
            '손익': [
                f"{korean_summary['total_profit_loss']:+,.0f}원",
                f"{us_summary['total_profit_loss_krw']:+,.0f}원",
                f"{total_profit:+,.0f}원"
            ]
        })

        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"전체 요약 데이터 조회 중 오류가 발생했습니다: {e}")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>보유종목 대시보드 | Powered by Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)
