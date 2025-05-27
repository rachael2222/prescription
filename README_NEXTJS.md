# 처방전 분석기 - Next.js + FastAPI 버전

## 🏗️ 프로젝트 구조

```
prescription/
├── backend/                 # FastAPI 백엔드
│   ├── main.py             # FastAPI 메인 애플리케이션
│   ├── medical_functions.py # 의료 분석 함수들
│   ├── config.py           # 설정 파일
│   ├── requirements.txt    # Python 의존성
│   └── Dockerfile         # 백엔드 배포용
├── frontend/               # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/           # App Router 페이지
│   │   ├── components/    # React 컴포넌트
│   │   └── lib/          # API 라이브러리
│   ├── package.json       # Node.js 의존성
│   ├── next.config.js     # Next.js 설정
│   ├── tailwind.config.js # Tailwind CSS 설정
│   └── vercel.json       # Vercel 배포 설정
└── README_NEXTJS.md       # 이 파일
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

### 2. 프론트엔드 설정 (Next.js)

```bash
# 새 터미널에서 프론트엔드 디렉토리로 이동
cd frontend

# Node.js 의존성 설치
npm install

# 환경 변수 설정 (.env.local 파일 생성)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Next.js 개발 서버 실행
npm run dev
```

## 🌐 Vercel 배포 방법

### 1. GitHub 저장소 준비
```bash
# 변경사항 커밋
git add .
git commit -m "Add Next.js frontend for Vercel deployment"
git push origin main
```

### 2. Vercel 배포

1. **Vercel 계정 생성**: [vercel.com](https://vercel.com)에서 GitHub 계정으로 로그인

2. **프로젝트 Import**:
   - "New Project" 클릭
   - GitHub 저장소 `rachael2222/prescription` 선택
   - Root Directory를 `frontend`로 설정

3. **환경 변수 설정**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```

4. **배포 설정**:
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

5. **Deploy** 버튼 클릭

### 3. 백엔드 배포 (Railway 추천)

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 백엔드 디렉토리에서
cd backend
railway login
railway init
railway up

# 환경 변수 설정
railway variables set OPENAI_API_KEY=your_key
railway variables set UPSTAGE_API_KEY=your_key
railway variables set DUR_API_KEY=your_key
```

## 🎨 주요 기능

### Next.js 프론트엔드
- ⚡ **App Router**: Next.js 13+ 최신 라우팅 시스템
- 🎨 **Tailwind CSS**: 유틸리티 기반 스타일링
- 📱 **반응형 디자인**: 모바일 최적화
- 🖱️ **드래그 앤 드롭**: 직관적인 파일 업로드
- 🎵 **음성 재생**: 분석 결과 음성 변환
- ⚡ **SSR/SSG**: 서버 사이드 렌더링 지원

### FastAPI 백엔드
- 🚀 **고성능 API**: 비동기 처리
- 📸 **OCR 처리**: Upstage API 연동
- 🤖 **AI 분석**: OpenAI GPT-4o
- 🔊 **TTS**: 텍스트-음성 변환
- 💾 **약품 정보**: DUR API 연동

## 🔧 API 엔드포인트

### 백엔드 API 문서
- Swagger UI: `https://your-backend-url/docs`
- ReDoc: `https://your-backend-url/redoc`

### 주요 엔드포인트
- `POST /api/analyze-prescription`: 처방전 이미지 분석
- `POST /api/text-to-speech`: 텍스트를 음성으로 변환
- `GET /api/drug-info/{drug_name}`: 특정 약품 정보 조회
- `GET /health`: 서버 상태 확인

## 🔒 보안 고려사항

1. **API 키 관리**: 환경 변수로 관리
2. **CORS 설정**: 프로덕션에서는 특정 도메인만 허용
3. **파일 업로드**: 이미지 파일만 허용, 크기 제한
4. **Next.js 보안**: 자동 XSS 방지, CSRF 보호

## 📈 성능 최적화

### Next.js 최적화
- **이미지 최적화**: Next.js Image 컴포넌트
- **코드 분할**: 자동 번들 분할
- **캐싱**: ISR (Incremental Static Regeneration)
- **압축**: 자동 Gzip 압축

### 배포 최적화
- **CDN**: Vercel Edge Network
- **빌드 최적화**: SWC 컴파일러
- **트리 쉐이킹**: 사용하지 않는 코드 제거

## 🛠️ 개발 팁

### Next.js 개발
- App Router 사용으로 최신 기능 활용
- TypeScript로 타입 안정성 확보
- Tailwind CSS로 빠른 스타일링
- React Server Components 활용

### 배포 팁
- Vercel은 Next.js에 최적화됨
- 환경 변수는 Vercel 대시보드에서 설정
- 프리뷰 배포로 테스트 후 프로덕션 배포

## 🐛 문제 해결

### 일반적인 문제들
1. **빌드 에러**: TypeScript 타입 에러 확인
2. **API 연결 실패**: 환경 변수 URL 확인
3. **Vercel 배포 실패**: 빌드 로그 확인
4. **CORS 에러**: 백엔드 CORS 설정 확인

### 로그 확인
- Next.js: `npm run dev` 콘솔 출력
- Vercel: 배포 로그 및 Function 로그
- 백엔드: FastAPI 서버 로그

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해주세요:
- 프론트엔드 관련: 브라우저 콘솔 에러와 함께 제보
- 백엔드 관련: API 로그와 함께 제보
- 배포 관련: Vercel 배포 로그와 함께 제보

## 🚀 배포 URL

- **프론트엔드**: https://your-app.vercel.app
- **백엔드**: https://your-backend.railway.app
- **GitHub**: https://github.com/rachael2222/prescription 