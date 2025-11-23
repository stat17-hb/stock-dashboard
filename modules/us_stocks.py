import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go


class USPortfolio:
    """해외 주식 포트폴리오 관리 클래스"""

    def __init__(self, exchange_rate=1350):
        """
        Args:
            exchange_rate: USD/KRW 환율 (기본값: 1350원)
        """
        # 보유주식수
        self.holdings = {
            'NVDA': 6,    # NVIDIA
            'GOOG': 5,    # Alphabet (Google)
            'AVGO': 4,    # Broadcom
            'OXY': 15     # Occidental Petroleum
        }

        # 평단가 (USD)
        self.avg_price = {
            'NVDA': 122.9667,
            'GOOG': 167.9600,
            'AVGO': 211.3750,
            'OXY': 48.5700
        }

        # 종목명 매핑
        self.stock_names = {
            'NVDA': 'NVIDIA Corporation',
            'GOOG': 'Alphabet Inc. (Google)',
            'AVGO': 'Broadcom Inc.',
            'OXY': 'Occidental Petroleum'
        }

        # 환율
        self.exchange_rate = exchange_rate

    def get_current_price(self, ticker):
        """주식 심볼을 입력받아 현재 가격을 반환하는 함수"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")

            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                return round(current_price, 2)
            else:
                return None

        except Exception as e:
            st.error(f"오류: {ticker} 조회 중 문제가 발생했습니다: {e}")
            return None

    def get_stock_info(self, ticker):
        """주식의 상세 정보를 조회하는 함수"""
        try:
            stock_obj = yf.Ticker(ticker)
            info = stock_obj.info

            stock_info = {
                'symbol': ticker,
                'name': info.get('longName', self.stock_names.get(ticker, 'N/A')),
                'current_price': info.get('currentPrice', self.get_current_price(ticker)),
                'previous_close': info.get('previousClose', 'N/A'),
                'day_change': info.get('regularMarketChange', 'N/A'),
                'day_change_percent': info.get('regularMarketChangePercent', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A')
            }

            return stock_info

        except Exception as e:
            st.error(f"오류: {ticker} 정보 조회 중 문제가 발생했습니다: {e}")
            return None

    def get_portfolio_summary(self):
        """포트폴리오 전체 요약 데이터 반환 (USD 및 KRW)"""
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
            'total_profit_loss': total_profit_loss,
            'total_investment_krw': total_investment * self.exchange_rate,
            'total_current_value_krw': total_current_value * self.exchange_rate,
            'total_profit_loss_krw': total_profit_loss * self.exchange_rate,
            'exchange_rate': self.exchange_rate
        }

    def get_historical_data(self, ticker, period="1mo"):
        """주식의 과거 데이터를 조회하는 함수"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            return hist
        except Exception as e:
            st.error(f"과거 데이터 조회 중 오류 발생: {e}")
            return None

    def display_dashboard(self):
        """Streamlit 대시보드 표시"""

        # 환율 설정
        exchange_rate_input = st.number_input(
            "환율 설정 (USD/KRW)",
            min_value=1000,
            max_value=2000,
            value=self.exchange_rate,
            step=10
        )
        self.exchange_rate = exchange_rate_input

        st.markdown("---")

        # 전체 포트폴리오 요약
        summary = self.get_portfolio_summary()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "총 투자금액",
                f"${summary['total_investment']:,.2f}",
                f"{summary['total_investment_krw']:,.0f}원"
            )

        with col2:
            st.metric(
                "현재 평가액",
                f"${summary['total_current_value']:,.2f}",
                f"{summary['total_current_value_krw']:,.0f}원"
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
                f"${summary['total_profit_loss']:+,.2f}",
                f"{summary['total_profit_loss_krw']:+,.0f}원"
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
                stock_name = self.stock_names[ticker]

                investment = buy_price * shares
                current_value = current_price * shares
                profit_loss = current_value - investment
                return_rate = (current_price - buy_price) / buy_price * 100

                portfolio_data.append({
                    '종목명': stock_name,
                    '티커': ticker,
                    '보유수량': f"{shares}주",
                    '평단가': f"${buy_price:.2f}",
                    '현재가': f"${current_price:.2f}",
                    '평가액': f"${current_value:,.2f}",
                    '평가액(원)': f"{current_value * self.exchange_rate:,.0f}원",
                    '수익률': f"{return_rate:+.2f}%",
                    '손익': f"${profit_loss:+,.2f}",
                    '손익(원)': f"{profit_loss * self.exchange_rate:+,.0f}원"
                })

        df = pd.DataFrame(portfolio_data)
        
        # 스타일링 적용
        styled_df = df.style.set_properties(**{
            'background-color': '#000000',
            'color': '#FF9800',
            'border-color': '#333333'
        }).map(lambda x: 'color: #00FF00' if '+' in str(x) else ('color: #FF0000' if '-' in str(x) else ''), subset=['수익률', '손익', '손익(원)'])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # 개별 종목 차트
        st.subheader("종목별 30일 가격 추이")

        for ticker in self.holdings:
            with st.expander(f"📈 {self.stock_names[ticker]} ({ticker})"):
                hist_data = self.get_historical_data(ticker, period="1mo")

                if hist_data is not None and not hist_data.empty:
                    # Plotly 캔들스틱 차트
                    fig = go.Figure(data=[go.Candlestick(
                        x=hist_data.index,
                        open=hist_data['Open'],
                        high=hist_data['High'],
                        low=hist_data['Low'],
                        close=hist_data['Close']
                    )])

                    fig.update_layout(
                        title=f"{self.stock_names[ticker]} 30일 가격 차트",
                        yaxis_title="가격 (USD)",
                        xaxis_title="날짜",
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 상세 정보
                    info = self.get_stock_info(ticker)
                    if info:
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            if info['previous_close'] != 'N/A':
                                st.metric("전일종가", f"${info['previous_close']:.2f}")
                            else:
                                st.metric("전일종가", "N/A")

                        with col2:
                            if info['52_week_high'] != 'N/A':
                                st.metric("52주 최고가", f"${info['52_week_high']:.2f}")
                            else:
                                st.metric("52주 최고가", "N/A")

                        with col3:
                            if info['52_week_low'] != 'N/A':
                                st.metric("52주 최저가", f"${info['52_week_low']:.2f}")
                            else:
                                st.metric("52주 최저가", "N/A")

                        with col4:
                            if info['pe_ratio'] != 'N/A':
                                st.metric("PER", f"{info['pe_ratio']:.2f}")
                            else:
                                st.metric("PER", "N/A")

                        # 추가 정보
                        if info['market_cap'] != 'N/A':
                            st.info(f"시가총액: ${info['market_cap']:,}")
                        if info['dividend_yield'] != 'N/A':
                            st.info(f"배당수익률: {info['dividend_yield']:.2%}")
                else:
                    st.warning(f"{self.stock_names[ticker]} 차트 데이터를 불러올 수 없습니다.")
