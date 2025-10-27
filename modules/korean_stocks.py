import streamlit as st
import pykrx.stock as stock
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go


class KoreanPortfolio:
    """국내 ETF 포트폴리오 관리 클래스"""

    def __init__(self):
        # 보유주식수
        self.holdings = {
            '132030': 250,  # KODEX 골드선물(H)
            '305080': 360,  # TIGER 미국채10년선물
            '360750': 476,  # TIGER 미국 S&P500
            '455890': 87    # RISE 머니마켓액티브
        }

        # 평단가
        self.avg_price = {
            '132030': 14930,  # KODEX 골드선물(H)
            '305080': 11959,  # TIGER 미국채10년선물
            '360750': 17945,  # TIGER 미국 S&P500
            '455890': 52359   # RISE 머니마켓액티브
        }

        # ETF 이름 매핑
        self.etf_names = {
            '132030': 'KODEX 골드선물(H)',
            '305080': 'TIGER 미국채10년선물',
            '360750': 'TIGER 미국 S&P500',
            '455890': 'RISE 머니마켓액티브'
        }

    def get_current_price(self, ticker):
        """ETF 티커를 입력받아 현재 가격을 반환하는 함수"""
        try:
            # 오늘 날짜
            today = datetime.now().strftime('%Y%m%d')

            # 주말인 경우 마지막 거래일로 조정
            if datetime.now().weekday() >= 5:  # 토요일(5) 또는 일요일(6)
                days_back = datetime.now().weekday() - 4
                today = (datetime.now() - timedelta(days=days_back)).strftime('%Y%m%d')

            # ETF 현재가 조회
            df = stock.get_etf_ohlcv_by_date(today, today, ticker)

            if not df.empty:
                price = df['종가'].iloc[-1]
                return int(price)
            else:
                return None

        except Exception as e:
            st.error(f"오류: {ticker} 조회 중 문제가 발생했습니다: {e}")
            return None

    def get_etf_info(self, ticker):
        """ETF의 상세 정보를 조회하는 함수"""
        try:
            # 오늘 날짜
            today = datetime.now().strftime('%Y%m%d')

            # 주말인 경우 마지막 거래일로 조정
            if datetime.now().weekday() >= 5:
                days_back = datetime.now().weekday() - 4
                today = (datetime.now() - timedelta(days=days_back)).strftime('%Y%m%d')

            # ETF OHLCV 데이터 조회
            df = stock.get_etf_ohlcv_by_date(today, today, ticker)

            if not df.empty:
                data = df.iloc[-1]

                etf_info = {
                    'ticker': ticker,
                    'name': self.etf_names.get(ticker, ticker),
                    'current_price': int(data['종가']),
                    'open_price': int(data['시가']),
                    'high_price': int(data['고가']),
                    'low_price': int(data['저가']),
                    'volume': int(data['거래량']),
                    'day_change': int(data['종가'] - data['시가']),
                    'day_change_percent': ((data['종가'] - data['시가']) / data['시가'] * 100) if data['시가'] != 0 else 0
                }

                return etf_info
            else:
                return None

        except Exception as e:
            st.error(f"오류: {ticker} 정보 조회 중 문제가 발생했습니다: {e}")
            return None

    def get_portfolio_summary(self):
        """포트폴리오 전체 요약 데이터 반환"""
        total_investment = 0
        total_current_value = 0

        for ticker in self.holdings:
            current_price = self.get_current_price(ticker)

            if current_price:
                buy_price = self.avg_price[ticker]
                shares = self.holdings[ticker]

                investment = buy_price * shares
                current_value = current_price * shares

                total_investment += investment
                total_current_value += current_value

        total_return = (total_current_value - total_investment) / total_investment * 100 if total_investment > 0 else 0
        total_profit_loss = total_current_value - total_investment

        return {
            'total_investment': total_investment,
            'total_current_value': total_current_value,
            'total_return': total_return,
            'total_profit_loss': total_profit_loss
        }

    def get_historical_data(self, ticker, days=30):
        """ETF의 과거 데이터를 조회하는 함수"""
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

            df = stock.get_etf_ohlcv_by_date(start_date, end_date, ticker)
            return df
        except Exception as e:
            st.error(f"과거 데이터 조회 중 오류 발생: {e}")
            return None

    def display_dashboard(self):
        """Streamlit 대시보드 표시"""

        # 전체 포트폴리오 요약
        summary = self.get_portfolio_summary()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "총 투자금액",
                f"{summary['total_investment']:,.0f}원"
            )

        with col2:
            st.metric(
                "현재 평가액",
                f"{summary['total_current_value']:,.0f}원"
            )

        with col3:
            st.metric(
                "총 수익률",
                f"{summary['total_return']:+.2f}%"
            )

        with col4:
            profit_color = "normal" if summary['total_profit_loss'] >= 0 else "inverse"
            st.metric(
                "총 손익",
                f"{summary['total_profit_loss']:+,.0f}원",
                delta=None
            )

        st.markdown("---")

        # 개별 종목 정보
        st.subheader("보유 종목 상세")

        portfolio_data = []

        for ticker in self.holdings:
            current_price = self.get_current_price(ticker)

            if current_price:
                buy_price = self.avg_price[ticker]
                shares = self.holdings[ticker]
                etf_name = self.etf_names[ticker]

                investment = buy_price * shares
                current_value = current_price * shares
                profit_loss = current_value - investment
                return_rate = (current_price - buy_price) / buy_price * 100

                portfolio_data.append({
                    '종목명': etf_name,
                    '티커': ticker,
                    '보유수량': f"{shares:,}주",
                    '평단가': f"{buy_price:,}원",
                    '현재가': f"{current_price:,}원",
                    '평가액': f"{current_value:,}원",
                    '수익률': f"{return_rate:+.2f}%",
                    '손익': f"{profit_loss:+,.0f}원"
                })

        df = pd.DataFrame(portfolio_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # 개별 종목 차트
        st.subheader("종목별 30일 가격 추이")

        for ticker in self.holdings:
            with st.expander(f"📈 {self.etf_names[ticker]} ({ticker})"):
                hist_data = self.get_historical_data(ticker, days=30)

                if hist_data is not None and not hist_data.empty:
                    # Plotly 캔들스틱 차트
                    fig = go.Figure(data=[go.Candlestick(
                        x=hist_data.index,
                        open=hist_data['시가'],
                        high=hist_data['고가'],
                        low=hist_data['저가'],
                        close=hist_data['종가']
                    )])

                    fig.update_layout(
                        title=f"{self.etf_names[ticker]} 30일 가격 차트",
                        yaxis_title="가격 (원)",
                        xaxis_title="날짜",
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 상세 정보
                    info = self.get_etf_info(ticker)
                    if info:
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("시가", f"{info['open_price']:,}원")
                        with col2:
                            st.metric("고가", f"{info['high_price']:,}원")
                        with col3:
                            st.metric("저가", f"{info['low_price']:,}원")
                        with col4:
                            st.metric("거래량", f"{info['volume']:,}주")
                else:
                    st.warning(f"{self.etf_names[ticker]} 차트 데이터를 불러올 수 없습니다.")
