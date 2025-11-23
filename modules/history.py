import pandas as pd
import streamlit as st

class TransactionHistory:
    def __init__(self):
        # Google Sheet URL and sheet name are now stored in Streamlit secrets
        # for security purposes. See .streamlit/secrets.toml for configuration.
        try:
            self.sheet_url = st.secrets["google_sheets"]["url"]
            self.sheet_name = st.secrets["google_sheets"]["sheet_name"]
        except (KeyError, FileNotFoundError):
            st.error("Google Sheets configuration not found in secrets. Please check .streamlit/secrets.toml")
            # Fallback to empty values
            self.sheet_url = ""
            self.sheet_name = ""

    def get_history(self):
        """구글 스프레드시트에서 거래내역을 가져옵니다."""
        try:
            # pandas는 URL에서 직접 엑셀 파일을 읽을 수 있습니다.
            df = pd.read_excel(self.sheet_url, sheet_name=self.sheet_name)
            
            # 데이터 전처리 (필요한 경우)
            # 예: 날짜 형식 변환, NaN 처리 등
            if '날짜' in df.columns:
                df['날짜'] = pd.to_datetime(df['날짜']).dt.strftime('%Y-%m-%d')
                
            return df
        except Exception as e:
            st.error(f"거래내역을 불러오는 중 오류가 발생했습니다: {e}")
            return pd.DataFrame()

    def get_accounts(self, df):
        """데이터프레임에서 계좌 목록을 추출합니다."""
        # '계좌', '증권사', 'Account' 등의 컬럼명을 찾습니다.
        account_col = None
        possible_names = ['계좌', '증권사', 'Account', 'account', '자산']
        
        for col in df.columns:
            if any(name in col for name in possible_names):
                account_col = col
                break
        
        if account_col:
            return df[account_col].unique().tolist(), account_col
        return [], None

    def style_dataframe(self, df):
        """데이터프레임에 블룸버그 스타일을 적용합니다."""
        if df.empty:
            return df
            
        # 모든 컬럼을 문자열로 변환하여 표시 (포맷팅 이슈 방지)
        display_df = df.astype(str)
        
        styled_df = display_df.style.set_properties(**{
            'background-color': '#131722',
            'color': '#D1D4DC',
            'border-color': '#2A2E39'
        })
        
        # 매수/매도 컬러링
        # '구분' 컬럼이 있거나, 데이터 내용 중에 '매수', '매도'가 있는 경우 처리
        def color_buy_sell(val):
            val_str = str(val)
            if '매수' in val_str:
                return 'color: #26a69a' # TradingView Green
            elif '매도' in val_str:
                return 'color: #ef5350' # TradingView Red
            return ''

        # 전체 데이터프레임에 대해 applymap을 쓰면 느릴 수 있으므로, 특정 컬럼이 있으면 그 컬럼만, 아니면 전체
        # 여기서는 간단하게 전체에 적용 (데이터가 크지 않다고 가정)
        styled_df = styled_df.map(color_buy_sell)
        
        return styled_df
