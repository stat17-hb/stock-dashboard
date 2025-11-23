import FinanceDataReader as fdr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

from modules.history import TransactionHistory

class PensionRebalancing:
    def __init__(self):
        # 자산 구성 및 목표 비중 정의
        # search_key: 구글 시트 '종목명' 매칭을 위한 키워드
        self.assets = {
            '360750': {'name': '미국S&P500', 'target_weight': 0.40, 'default_shares': 476, 'search_key': '미국S&P500'},
            '132030': {'name': '골드선물', 'target_weight': 0.25, 'default_shares': 250, 'search_key': '골드선물'},
            '305080': {'name': '미국채10년', 'target_weight': 0.10, 'default_shares': 360, 'search_key': '미국채10년'},
            '455890': {'name': 'MMF', 'target_weight': 0.10, 'default_shares': 87, 'search_key': '머니마켓'},
            '195980': {'name': 'MSCI신흥국', 'target_weight': 0.15, 'default_shares': 0, 'search_key': 'MSCI신흥국'}
        }
        self.tickers = list(self.assets.keys())

    def calculate_holdings(self):
        """거래내역을 기반으로 현재 보유 수량을 계산합니다."""
        try:
            history = TransactionHistory()
            df = history.get_history()
            
            if df.empty:
                return {}

            # 계좌 컬럼 찾기
            accounts, account_col = history.get_accounts(df)
            if not account_col:
                return {}

            # '연금저축'이 포함된 계좌 필터링
            pension_account = None
            for acc in accounts:
                if '연금저축' in str(acc):
                    pension_account = acc
                    break
            
            if not pension_account:
                st.warning("계좌 목록에서 '연금저축' 계좌를 찾을 수 없습니다.")
                return {}

            # 해당 계좌의 거래내역만 필터링
            df_pension = df[df[account_col] == pension_account].copy()
            
            # 보유 수량 계산
            current_holdings = {}
            
            # 종목명이나 코드로 매칭
            name_col = None
            qty_col = None
            type_col = None # 매수/매도 구분
            
            for col in df_pension.columns:
                if '종목명' in col or '종목' in col:
                    name_col = col
                if '수량' in col or '주수' in col:
                    qty_col = col
                if '구분' in col or '거래' in col: # 매수/매도
                    type_col = col
            
            if not (name_col and qty_col):
                return {}

            # 자산별 수량 합산
            for ticker, info in self.assets.items():
                search_key = info.get('search_key', info['name'])
                
                # 종목명에 검색 키워드가 포함된 행 필터링
                asset_df = df_pension[df_pension[name_col].astype(str).str.contains(search_key, na=False)]
                
                total_qty = 0
                for _, row in asset_df.iterrows():
                    qty = pd.to_numeric(row[qty_col], errors='coerce')
                    if pd.isna(qty): continue
                    
                    trade_type = str(row[type_col]) if type_col else ''
                    
                    if '매수' in trade_type:
                        total_qty += qty
                    elif '매도' in trade_type:
                        total_qty -= qty
                    else:
                        total_qty += qty
                
                current_holdings[ticker] = int(total_qty)
                
            return current_holdings

        except Exception as e:
            st.error(f"보유 수량 계산 중 오류 발생: {e}")
            return {}

    def get_current_prices(self):
        """현재가 조회"""
        prices = {}
        today = datetime.now()
        
        for ticker in self.tickers:
            try:
                # 오늘 날짜로 먼저 조회
                df = fdr.DataReader(ticker, today.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
                
                # 데이터가 없으면 전일 데이터 조회 (최대 5일 전까지 시도)
                if len(df) == 0:
                    for i in range(1, 6):
                        past_day = today - timedelta(days=i)
                        df = fdr.DataReader(ticker, past_day.strftime('%Y%m%d'), past_day.strftime('%Y%m%d'))
                        if len(df) > 0:
                            break
                
                if len(df) > 0:
                    prices[ticker] = df['Close'].iloc[-1]
                else:
                    prices[ticker] = 0 # 가격 조회 실패 시 0 처리 혹은 에러 처리
            except Exception as e:
                st.error(f"{self.assets[ticker]['name']} ({ticker}) 가격 조회 실패: {e}")
                prices[ticker] = 0
                
        return prices

    def calculate_rebalancing(self, current_shares_input):
        """리밸런싱 계산"""
        prices = self.get_current_prices()
        
        # 데이터 준비
        data = []
        total_value = 0
        
        # 1. 현재 가치 계산
        for ticker, info in self.assets.items():
            current_shares = current_shares_input.get(ticker, info['default_shares'])
            price = prices.get(ticker, 0)
            current_value = current_shares * price
            total_value += current_value
            
            data.append({
                'ticker': ticker,
                'name': info['name'],
                'price': price,
                'current_shares': current_shares,
                'current_value': current_value,
                'target_weight': info['target_weight']
            })
            
        # 2. 리밸런싱 계산
        results = []
        after_total_value = 0
        
        for item in data:
            # 현재 비중
            current_weight = item['current_value'] / total_value if total_value > 0 else 0
            
            # 목표 금액 및 수량
            target_value = total_value * item['target_weight']
            target_shares = int(target_value / item['price']) if item['price'] > 0 else 0
            
            # 매수/매도 수량
            shares_diff = target_shares - item['current_shares']
            
            # 리밸런싱 후 예상 금액
            after_value = target_shares * item['price']
            after_total_value += after_value
            
            results.append({
                '자산명': item['name'],
                '현재가': item['price'],
                '현재 보유(주)': item['current_shares'],
                '현재 비중': current_weight,
                '목표 수량(주)': target_shares,
                '목표 비중': item['target_weight'],
                '매수/매도': shares_diff,
                '현재 보유금액(원)': item['current_value'],
                '리밸런싱 후 금액(원)': after_value,
                '예상 거래금액(원)': abs(shares_diff * item['price'])
            })
            
        df = pd.DataFrame(results)
        return df, total_value, after_total_value

    def display_dashboard(self):
        """대시보드 표시"""
        st.subheader("📊 연금저축펀드 리밸런싱 분석")
        
        # 보유 수량 자동 계산
        calculated_holdings = self.calculate_holdings()
        
        # 입력 폼 생성
        with st.expander("보유 수량 입력 (자동 계산됨)", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            cols = [col1, col2, col3, col4, col5]
            
            current_shares_input = {}
            
            for i, (ticker, info) in enumerate(self.assets.items()):
                # 계산된 수량이 있으면 그것을 기본값으로, 없으면 0 (또는 기존 default)
                default_val = calculated_holdings.get(ticker, info['default_shares'])
                
                with cols[i % 5]:
                    shares = st.number_input(
                        f"{info['name']}",
                        min_value=0,
                        value=default_val,
                        key=f"shares_{ticker}"
                    )
                    current_shares_input[ticker] = shares
        
        # 계산 실행
        if st.button("리밸런싱 계산", type="primary"):
            with st.spinner('현재가 조회 및 리밸런싱 계산 중...'):
                df, total_val, after_total = self.calculate_rebalancing(current_shares_input)
                
                # 요약 메트릭
                m1, m2, m3 = st.columns(3)
                m1.metric("총 자산", f"{total_val:,.0f}원")
                m2.metric("리밸런싱 후 예상 자산", f"{after_total:,.0f}원")
                diff_val = after_total - total_val
                m3.metric("자투리 금액 차이", f"{diff_val:,.0f}원", delta_color="off")
                
                st.markdown("---")
                
                # 테이블 표시를 위한 포맷팅
                display_df = df.copy()
                display_df['현재가'] = display_df['현재가'].apply(lambda x: f"{x:,.0f}")
                display_df['현재 비중'] = display_df['현재 비중'].apply(lambda x: f"{x:.1%}")
                display_df['목표 비중'] = display_df['목표 비중'].apply(lambda x: f"{x:.1%}")
                display_df['매수/매도'] = display_df['매수/매도'].apply(lambda x: f"{x:+d}")
                display_df['현재 보유금액(원)'] = display_df['현재 보유금액(원)'].apply(lambda x: f"{x:,.0f}")
                display_df['리밸런싱 후 금액(원)'] = display_df['리밸런싱 후 금액(원)'].apply(lambda x: f"{x:,.0f}")
                
                # 예상 거래금액에 매수/매도 텍스트 추가
                def format_trade_amount(row):
                    amount = row['예상 거래금액(원)']
                    action = "매수" if int(row['매수/매도']) > 0 else "매도" if int(row['매수/매도']) < 0 else "-"
                    if action == "-":
                        return "-"
                    return f"{amount:,.0f} ({action})"
                
                display_df['예상 거래금액(원)'] = df.apply(format_trade_amount, axis=1)
                
                # 주요 컬럼만 선택하여 표시
                cols_to_show = ['자산명', '현재 보유(주)', '현재 비중', '목표 수량(주)', '목표 비중', '매수/매도', '현재 보유금액(원)', '리밸런싱 후 금액(원)', '예상 거래금액(원)']
                
                # 스타일링 적용
                styled_df = display_df[cols_to_show].style.set_properties(**{
                    'background-color': '#131722',
                    'color': '#D1D4DC',
                    'border-color': '#2A2E39'
                }).map(lambda x: 'color: #26a69a' if '매수' in str(x) else ('color: #ef5350' if '매도' in str(x) else ''), subset=['예상 거래금액(원)']) \
                  .map(lambda x: 'color: #26a69a' if '+' in str(x) else ('color: #ef5350' if '-' in str(x) else ''), subset=['매수/매도'])

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # 차트 시각화
                st.markdown("### 📈 비중 변화 시각화")
                chart_data = df[['자산명', '현재 비중', '목표 비중']].set_index('자산명')
                st.bar_chart(chart_data)
