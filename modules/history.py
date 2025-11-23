import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

class TransactionHistory:
    def __init__(self):
        # Google Sheets API를 사용한 안전한 인증 방식
        # 서비스 계정 키는 .streamlit/secrets.toml에 저장됩니다
        try:
            # Streamlit secrets에서 서비스 계정 정보 가져오기
            credentials_dict = dict(st.secrets["gcp_service_account"])
            self.sheet_name = st.secrets["google_sheets"]["sheet_name"]
            self.spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]

            # Google Sheets API 인증
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly"
            ]
            credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
            self.gc = gspread.authorize(credentials)

        except KeyError as e:
            st.error(f"Google Sheets configuration not found in secrets: {e}")
            st.info("Please restart the Streamlit app to load the secrets configuration.")
            # Fallback to None
            self.gc = None
            self.sheet_name = ""
            self.spreadsheet_id = ""
        except Exception as e:
            st.error(f"Error loading secrets: {type(e).__name__}: {e}")
            # Fallback to None
            self.gc = None
            self.sheet_name = ""
            self.spreadsheet_id = ""

    def get_history(self):
        """구글 스프레드시트에서 거래내역을 가져옵니다 (Google Sheets API 사용)."""
        try:
            if not self.gc:
                st.warning("Google Sheets API 인증이 설정되지 않았습니다.")
                return pd.DataFrame()

            # 스프레드시트 열기
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)

            # 특정 시트 선택
            worksheet = spreadsheet.worksheet(self.sheet_name)

            # 데이터를 DataFrame으로 변환
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)

            # 데이터 전처리 (필요한 경우)
            if '날짜' in df.columns:
                df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.strftime('%Y-%m-%d')

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
