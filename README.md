# 📊 보유종목 대시보드 (Stock Dashboard)

국내 ETF, 해외 주식, 그리고 연금저축 포트폴리오를 통합 관리하고 실시간으로 모니터링하는 Streamlit 기반 대시보드입니다.

## 🚀 주요 기능

### 1. 국내 ETF 포트폴리오
- **실시간 가격 조회**: `pykrx`를 활용한 한국 ETF 실시간 가격 모니터링
- **보유 종목 관리**: KODEX 골드선물(H), TIGER 미국채10년선물 등 주요 ETF
- **투자 성과 분석**: 평단가 대비 수익률, 손익금 계산 및 시각화
- **차트**: 30일 캔들스틱 차트 및 상세 OHLCV 데이터 제공

### 2. 해외 주식 포트폴리오
- **실시간 가격 조회**: `yfinance`를 활용한 미국 주식 실시간 가격 모니터링
- **주요 종목**: NVIDIA, Google, Broadcom 등
- **환율 연동**: USD/KRW 환율 실시간 적용 및 수동 설정 가능
- **심층 분석**: 52주 최고/최저가, PER, 배당수익률 등 투자 지표 제공

### 3. 연금저축 리밸런싱 (New!)
- **구글 시트 연동**: 구글 시트의 거래 내역을 자동으로 불러와 현재 보유량 계산
- **리밸런싱 가이드**: 목표 비중 대비 현재 비중을 분석하여 매수/매도 수량 추천
- **자산 배분**: 현재 자산 배분 현황 시각화

### 4. 전체 포트폴리오 요약
- 국내/해외/연금 계좌 통합 자산 현황
- 총 투자금액, 평가금액, 누적 수익률 대시보드
- 자산군별(주식, 채권, 원자재 등) 비중 분석

## 📋 사전 요구사항

- Python 3.10 이상 권장
- Google Cloud Platform 서비스 계정 키 (연금저축 연동 시 필요)

## 🛠️ 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/stat17-hb/stock-dashboard.git
cd stock-dashboard
```

### 2. 가상환경 생성 및 패키지 설치

#### 옵션 A: Conda 사용 (권장)

```bash
# 가상환경 생성
conda create -n stock-dashboard python=3.10 -y

# 가상환경 활성화
conda activate stock-dashboard

# 패키지 설치
pip install -r requirements.txt
```

#### 옵션 B: venv 사용

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

## 🎯 실행 방법

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며, 다음 주소로 접속할 수 있습니다:
- 로컬: http://localhost:8501

## 📂 프로젝트 구조

```
stock-dashboard/
├── app.py                      # Streamlit 메인 애플리케이션
├── modules/
│   ├── __init__.py
│   ├── korean_stocks.py        # 국내 ETF 포트폴리오 모듈
│   ├── us_stocks.py            # 해외 주식 포트폴리오 모듈
│   ├── pension.py              # 연금저축 리밸런싱 모듈 (Google Sheets 연동)
│   └── history.py              # 자산 히스토리 관리 모듈
├── .streamlit/
│   └── config.toml             # Streamlit 테마 및 서버 설정
├── requirements.txt            # Python 패키지 의존성
└── README.md                   # 프로젝트 문서
```

## 🔧 설정 방법

### 1. 포트폴리오 종목 설정
`modules/` 폴더 내의 각 파이썬 파일(`korean_stocks.py`, `us_stocks.py`)에서 `holdings`(보유수량) 및 `avg_price`(평단가) 딕셔너리를 수정하여 자신의 포트폴리오를 반영할 수 있습니다.

### 2. 구글 시트 연동 (연금저축) - 필수 설정

#### 🔐 보안 설정: Google Sheets API + 서비스 계정

**이 방법의 장점:**
- ✅ Google Sheets를 "제한됨" (특정 사용자만)으로 설정 가능
- ✅ 공개 URL 노출 없이 안전하게 데이터 접근
- ✅ 세밀한 권한 제어 (읽기 전용 등)

#### 📋 단계별 설정 가이드

**Step 1: Google Cloud 프로젝트 및 서비스 계정 생성**

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스 > 라이브러리**로 이동하여 다음 API 활성화:
   - Google Sheets API
   - Google Drive API

4. **IAM 및 관리자 > 서비스 계정**으로 이동
5. "서비스 계정 만들기" 클릭:
   - 서비스 계정 이름: `stock-dashboard-reader` (원하는 이름)
   - 역할: "기본" (권한 불필요)
   - "완료" 클릭

6. 생성된 서비스 계정 클릭 > **키** 탭으로 이동
7. "키 추가" > "새 키 만들기" > **JSON** 선택 > "만들기"
8. JSON 키 파일 다운로드 (안전한 곳에 보관!)

**Step 2: Google Sheets 권한 설정**

1. Google Sheets를 엽니다
2. 주소창에서 **스프레드시트 ID**를 복사합니다
   - 예: `https://docs.google.com/spreadsheets/d/1Hppkoz7zbZlSCEwPR0vzCRV94eP6c7j9udaE0qKXtws/edit`
   - ID: `1Hppkoz7zbZlSCEwPR0vzCRV94eP6c7j9udaE0qKXtws`

3. 우측 상단 "공유" 버튼 클릭
4. 서비스 계정 이메일 추가:
   - 형식: `stock-dashboard-reader@프로젝트ID.iam.gserviceaccount.com`
   - 권한: **뷰어** (읽기 전용)
5. **완료** 클릭

**Step 3: Streamlit Secrets 설정**

1. 프로젝트의 `.streamlit/secrets.toml` 파일 생성 (또는 `secrets.toml.example` 복사)

2. 다운로드한 JSON 키 파일을 열어 내용을 `secrets.toml`에 다음과 같이 입력:

```toml
[google_sheets]
spreadsheet_id = "YOUR_SPREADSHEET_ID"  # Step 2에서 복사한 ID
sheet_name = "2.거래내역"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
universe_domain = "googleapis.com"
```

3. **중요**: JSON 파일의 값을 그대로 복사하세요 (특히 `private_key`는 줄바꿈 `\n` 포함)

**Step 4: 패키지 설치 및 실행**

```bash
# 새로운 패키지 설치
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run app.py
```

#### 🔒 보안 체크리스트

- ✅ `.gitignore`에 `secrets.toml`이 포함되어 있는지 확인 (이미 포함됨)
- ✅ **절대로** `secrets.toml` 파일을 Git에 커밋하지 마세요
- ✅ JSON 키 파일을 안전하게 보관하세요 (외부 공유 금지)
- ✅ Google Sheets 공유 설정을 "제한됨"으로 변경 (서비스 계정만 접근)
- ✅ 서비스 계정 권한을 "뷰어"(읽기 전용)로 제한

## 📊 사용 기술

- **Frontend**: Streamlit
- **Data Source**: pykrx (국내), yfinance (해외), FinanceDataReader
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly Interactive Charts
- **Integration**: Google Sheets API (gspread)

## ⚠️ 주의사항

1. **API 제한**: 무료 데이터 소스를 사용하므로 과도한 요청 시 일시적으로 차단될 수 있습니다.
2. **데이터 지연**: 실시간 데이터는 거래소 사정에 따라 15~20분 지연될 수 있습니다.
3. **투자 책임**: 본 대시보드는 정보 제공용이며, 실제 투자의 책임은 사용자에게 있습니다.

## 📝 라이선스

MIT License

---

**Powered by Streamlit | Developed by [stat17-hb](https://github.com/stat17-hb)**
