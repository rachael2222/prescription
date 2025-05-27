# 🚀 Railway 배포 가이드 (5분 완성)

## 1단계: Railway 계정 생성
1. [railway.app](https://railway.app) 방문
2. "Start a New Project" 클릭
3. GitHub 계정으로 로그인

## 2단계: 프로젝트 배포
1. "Deploy from GitHub repo" 선택
2. `rachael2222/prescription` 저장소 선택
3. **중요**: Root Directory를 `backend`로 설정

## 3단계: 환경변수 설정
Variables 탭에서 다음 추가:
```
OPENAI_API_KEY=sk-your-actual-openai-key
UPSTAGE_API_KEY=up_your-actual-upstage-key
DUR_API_KEY=your-actual-dur-key
DUR_API_BASE_URL=http://apis.data.go.kr/1471000/DURPrdlstInfoService03
```

## 4단계: 도메인 생성
1. Settings → Networking
2. "Generate Domain" 클릭
3. URL 복사 (예: `https://your-app.railway.app`)

## 5단계: 프론트엔드 연결
프로젝트 루트에 `.env.local` 파일 생성:
```
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

## 6단계: Vercel 재배포
```bash
git add .
git commit -m "Connect to Railway backend"
git push
```

## ✅ 완료!
- 로컬 속도: ⚡ 즉시 응답
- Railway 속도: ⚡ 1-2초 응답  
- Vercel API: 🐌 5-10초 응답

## 💡 API 키 발급 방법
- **OpenAI**: [platform.openai.com](https://platform.openai.com/api-keys)
- **Upstage**: [console.upstage.ai](https://console.upstage.ai)
- **DUR API**: [data.go.kr](https://www.data.go.kr) 회원가입 후 신청 