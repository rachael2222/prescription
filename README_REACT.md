# 처방전 분석기 - React + FastAPI 버전

## 🏗️ 프로젝트 구조

```
prescription/
├── backend/                 # FastAPI 백엔드
│   ├── main.py             # FastAPI 메인 애플리케이션
│   ├── medical_functions.py # 의료 분석 함수들
│   ├── config.py           # 설정 파일
│   ├── requirements.txt    # Python 의존성
│   └── Dockerfile         # 백엔드 배포용
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── App.js         # 메인 React 컴포넌트
│   │   ├── App.css        # 스타일시트
│   │   └── index.js       # React 엔트리포인트
│   ├── package.json       # Node.js 의존성
│   └── public/            # 정적 파일들
└── README_REACT.md        # 이 파일
```

## 🚀 로컬 개발 환경 설정

### 1. 백엔드 설정 (FastAPI)

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성)
OPENAI_API_KEY=your_openai_api_key
UPSTAGE_API_KEY=your_upstage_api_key
DUR_API_KEY=your_dur_api_key
DUR_API_BASE_URL=http://apis.data.go.kr/1471000/DURPrdlstInfoService03

# 백엔드 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 프론트엔드 설정 (React)

```bash
# 새 터미널에서 프론트엔드 디렉토리로 이동
cd frontend

# Node.js 의존성 설치
npm install

# 환경 변수 설정 (.env 파일 생성)
REACT_APP_API_URL=http://localhost:8000

# React 개발 서버 실행
npm start
```

## 🌐 배포 방법

### 백엔드 배포 (Railway/Heroku/DigitalOcean)

1. **Railway 배포**:
   ```bash
   # Railway CLI 설치
   npm install -g @railway/cli
   
   # 로그인 및 프로젝트 생성
   railway login
   railway init
   
   # 환경 변수 설정
   railway variables set OPENAI_API_KEY=your_key
   railway variables set UPSTAGE_API_KEY=your_key
   railway variables set DUR_API_KEY=your_key
   
   # 배포
   railway up
   ```

2. **Heroku 배포**:
   ```bash
   # Heroku CLI 설치 후
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set UPSTAGE_API_KEY=your_key
   heroku config:set DUR_API_KEY=your_key
   git push heroku main
   ```

### 프론트엔드 배포 (Vercel/Netlify)

1. **Vercel 배포**:
   ```bash
   # Vercel CLI 설치
   npm install -g vercel
   
   # 프론트엔드 디렉토리에서
   cd frontend
   vercel
   
   # 환경 변수 설정 (Vercel 대시보드에서)
   REACT_APP_API_URL=https://your-backend-url.railway.app
   ```

2. **Netlify 배포**:
   - GitHub 저장소 연결
   - Build command: `npm run build`
   - Publish directory: `build`
   - 환경 변수에 `REACT_APP_API_URL` 설정

## 🔧 API 엔드포인트

### 백엔드 API 문서

백엔드 서버 실행 후 다음 URL에서 API 문서 확인:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 주요 엔드포인트

- `POST /api/analyze-prescription`: 처방전 이미지 분석
- `POST /api/text-to-speech`: 텍스트를 음성으로 변환
- `GET /api/drug-info/{drug_name}`: 특정 약품 정보 조회
- `GET /health`: 서버 상태 확인

## 🎨 주요 기능

### 프론트엔드 (React)
- 📱 반응형 웹 디자인
- 🖱️ 드래그 앤 드롭 파일 업로드
- 🎵 음성 재생 기능
- 📊 실시간 분석 결과 표시
- 💊 약품 목록 시각화

### 백엔드 (FastAPI)
- 🚀 고성능 비동기 API
- 📸 이미지 OCR 처리
- 🤖 AI 기반 텍스트 분석
- 🔊 텍스트-음성 변환
- 💾 약품 안전정보 조회

## 🔒 보안 고려사항

1. **API 키 관리**: 환경 변수로 관리, 코드에 하드코딩 금지
2. **CORS 설정**: 프로덕션에서는 특정 도메인만 허용
3. **파일 업로드**: 이미지 파일만 허용, 크기 제한
4. **에러 처리**: 민감한 정보 노출 방지

## 🛠️ 개발 팁

### 백엔드 개발
- FastAPI의 자동 문서 생성 활용
- Pydantic 모델로 데이터 검증
- 비동기 처리로 성능 최적화

### 프론트엔드 개발
- React Hooks 활용한 상태 관리
- Axios로 API 통신
- CSS Grid/Flexbox로 반응형 레이아웃

## 📈 확장 가능성

1. **사용자 인증**: JWT 토큰 기반 로그인
2. **데이터베이스**: PostgreSQL/MongoDB 연동
3. **캐싱**: Redis로 분석 결과 캐싱
4. **모니터링**: Sentry, DataDog 연동
5. **테스트**: Jest(프론트), pytest(백엔드)

## 🐛 문제 해결

### 일반적인 문제들

1. **CORS 에러**: 백엔드 CORS 설정 확인
2. **API 연결 실패**: 환경 변수 URL 확인
3. **파일 업로드 실패**: 파일 크기 및 형식 확인
4. **음성 재생 안됨**: 브라우저 자동재생 정책 확인

### 로그 확인
- 백엔드: `uvicorn main:app --log-level debug`
- 프론트엔드: 브라우저 개발자 도구 Console 탭

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해주세요.
- 백엔드 관련: API 로그와 함께 제보
- 프론트엔드 관련: 브라우저 콘솔 에러와 함께 제보 