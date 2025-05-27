# 🏥 처방전 분석기 - AI 기반 의료 정보 서비스

Next.js + FastAPI로 구축된 현대적인 처방전 분석 웹 애플리케이션입니다.

## 🚀 주요 기능

- 📸 **OCR 기술**: 처방전 이미지에서 텍스트 자동 추출
- 🤖 **AI 분석**: OpenAI GPT-4o를 활용한 지능형 약품 정보 분석
- 🔊 **음성 변환**: 분석 결과를 음성으로 제공
- 💊 **약품 안전정보**: DUR API 연동으로 약품 상호작용 정보 제공
- 📱 **반응형 디자인**: 모바일 최적화된 사용자 인터페이스

## 🛠️ 기술 스택

### Frontend
- **Next.js 14**: React 기반 풀스택 프레임워크
- **TypeScript**: 타입 안정성
- **Tailwind CSS**: 유틸리티 기반 스타일링
- **React Hooks**: 상태 관리

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **OpenAI API**: GPT-4o 모델
- **Upstage API**: OCR 텍스트 추출
- **DUR API**: 약품 안전정보
- **gTTS**: 텍스트-음성 변환

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/rachael2222/prescription.git
cd prescription
```

### 2. 프론트엔드 설정
```bash
# 의존성 설치
npm install

# 환경 변수 설정 (.env.local 파일 생성)
NEXT_PUBLIC_API_URL=http://localhost:8000

# 개발 서버 실행
npm run dev
```

### 3. 백엔드 설정
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

# 백엔드 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 배포

### Vercel (프론트엔드)
1. [Vercel](https://vercel.com)에서 GitHub 저장소 연결
2. 자동으로 Next.js 프로젝트 감지
3. 환경 변수 `NEXT_PUBLIC_API_URL` 설정
4. 배포 완료!

### Railway/Heroku (백엔드)
```bash
# Railway 배포 예시
cd backend
railway login
railway init
railway up
```

## 📁 프로젝트 구조

```
prescription/
├── src/                    # Next.js 소스 코드
│   ├── app/               # App Router 페이지
│   ├── components/        # React 컴포넌트
│   └── lib/              # 유틸리티 및 API
├── backend/               # FastAPI 백엔드
│   ├── main.py           # FastAPI 애플리케이션
│   ├── medical_functions.py # 의료 분석 함수
│   └── requirements.txt  # Python 의존성
├── public/               # 정적 파일
├── samples/              # 샘플 처방전 이미지
├── package.json          # Node.js 의존성
├── next.config.js        # Next.js 설정
└── README.md            # 이 파일
```

## 🔒 보안

- API 키는 환경 변수로 관리
- CORS 설정으로 안전한 API 통신
- 파일 업로드 검증 및 제한

## 📞 지원

문제가 발생하면 [GitHub Issues](https://github.com/rachael2222/prescription/issues)에 등록해주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**⚠️ 주의사항**: 본 서비스는 참고용이며, 정확한 의료 정보는 전문의와 상담하시기 바랍니다. 