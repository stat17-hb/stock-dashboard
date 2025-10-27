# 📊 보유종목 대시보드

국내 ETF와 해외 주식 포트폴리오를 실시간으로 모니터링하는 Streamlit 기반 대시보드입니다.

## 🚀 주요 기능

### 국내 ETF 포트폴리오
- **실시간 가격 조회**: pykrx를 활용한 한국 ETF 실시간 가격
- **보유 종목**: KODEX 골드선물(H), TIGER 미국채10년선물, TIGER 미국 S&P500, RISE 머니마켓액티브
- **상세 정보**: 평단가, 수익률, 손익 계산
- **차트**: 30일 캔들스틱 차트 및 상세 OHLCV 데이터

### 해외 주식 포트폴리오
- **실시간 가격 조회**: yfinance를 활용한 미국 주식 실시간 가격
- **보유 종목**: NVIDIA (NVDA), Alphabet (GOOG), Broadcom (AVGO), Occidental Petroleum (OXY)
- **환율 변환**: USD/KRW 환율 설정 기능
- **상세 정보**: 평단가, 수익률, 손익 (달러 및 원화)
- **차트**: 30일 캔들스틱 차트, 52주 최고/최저가, PER, 배당수익률 등

### 전체 포트폴리오 요약
- 국내 ETF + 해외 주식 통합 대시보드
- 총 투자금액, 현재 자산, 수익률 비교
- 포트폴리오 구성 비율 시각화
- 자산별 수익률 비교 차트

## 📋 사전 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)

## 🛠️ 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/stat17-hb/stock-dashboard.git
cd stock-dashboard
```

### 2. 가상환경 생성 (권장)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 필요한 패키지 설치

```bash
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
│   └── us_stocks.py            # 해외 주식 포트폴리오 모듈
├── requirements.txt            # Python 패키지 의존성
├── .gitignore                  # Git 제외 파일 목록
└── README.md                   # 프로젝트 문서
```

## 🔧 설정 방법

### 보유 종목 변경

#### 국내 ETF 종목 변경
[modules/korean_stocks.py](modules/korean_stocks.py)의 `KoreanPortfolio` 클래스에서 수정:

```python
self.holdings = {
    '132030': 250,  # KODEX 골드선물(H)
    '305080': 360,  # TIGER 미국채10년선물
    # ... 티커 코드와 보유 수량 수정
}

self.avg_price = {
    '132030': 14930,  # 평단가
    '305080': 11959,
    # ... 평단가 수정
}

self.etf_names = {
    '132030': 'KODEX 골드선물(H)',  # ETF 이름
    '305080': 'TIGER 미국채10년선물',
    # ... 이름 수정
}
```

#### 해외 주식 종목 변경
[modules/us_stocks.py](modules/us_stocks.py)의 `USPortfolio` 클래스에서 수정:

```python
self.holdings = {
    'NVDA': 6,    # 티커와 보유 수량
    'GOOG': 5,
    # ... 수정
}

self.avg_price = {
    'NVDA': 122.9667,  # 평단가 (USD)
    'GOOG': 167.9600,
    # ... 수정
}

self.stock_names = {
    'NVDA': 'NVIDIA Corporation',  # 주식 이름
    'GOOG': 'Alphabet Inc. (Google)',
    # ... 수정
}
```

### 환율 설정
대시보드 실행 후 "해외 주식" 탭에서 환율을 직접 입력하여 변경할 수 있습니다.

## 📊 사용 기술

- **Streamlit**: 웹 대시보드 프레임워크
- **pykrx**: 한국 증권 시장 데이터 API
- **yfinance**: 미국 주식 시장 데이터 API
- **pandas**: 데이터 분석 및 처리
- **plotly**: 인터랙티브 차트 시각화

## 🔄 자동 새로고침

대시보드 좌측 사이드바에서 "자동 새로고침 (60초)" 옵션을 활성화하면 1분마다 자동으로 데이터가 갱신됩니다.

## ⚠️ 주의사항

1. **거래 시간**: 국내 ETF는 한국 증시 거래 시간(09:00-15:30 KST), 해외 주식은 미국 증시 거래 시간(09:30-16:00 EST)에만 실시간 가격이 업데이트됩니다.

2. **주말/공휴일**: 주말이나 공휴일에는 마지막 거래일의 종가가 표시됩니다.

3. **API 제한**: yfinance 및 pykrx는 무료 API이므로 과도한 호출 시 제한이 있을 수 있습니다.

4. **데이터 정확성**: 표시되는 데이터는 참고용이며, 실제 투자 결정 시 증권사의 공식 데이터를 확인하세요.

## 📝 라이선스

MIT License

## 🤝 기여하기

이슈 제출 및 Pull Request를 환영합니다!

## 📧 문의

프로젝트 관련 문의사항은 GitHub Issues를 통해 남겨주세요.

---

**Powered by Streamlit | Data from pykrx & yfinance**
