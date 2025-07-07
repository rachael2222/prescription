# 🏥 처방전 분석기 - AI 기반 의료 정보 서비스

Streamlit으로 구축된 사용자 친화적인 처방전 분석 웹 애플리케이션입니다.

## 🚀 주요 기능

- 📸 **OCR 기술**: 처방전 이미지에서 텍스트 자동 추출 (Upstage API)
- 🤖 **AI 분석**: OpenAI GPT-4를 활용한 지능형 약품 정보 분석  
- 💊 **약품 안전정보**: DUR API 연동으로 약품 상호작용 정보 제공
- 🔊 **음성 변환**: 분석 결과를 음성으로 제공 (gTTS)
- 📱 **SMS 공유**: 분석 결과를 모바일로 전송
- 🌐 **웹 기반**: 브라우저에서 바로 사용 가능

## 🛠️ 기술 스택

- **Streamlit**: Python 기반 웹 애플리케이션 프레임워크
- **OpenAI API**: GPT-4 모델을 활용한 텍스트 분석
- **ocr API**: OCR 텍스트 추출
- **식약청 API**: 약품 안전정보 조회
- **gTTS**: 텍스트-음성 변환
- **Pillow**: 이미지 처리
- **Pandas/Numpy**: 데이터 처리

## 🌐 온라인 사용

**🔗 배포된 앱**: [Streamlit Community Cloud에서 바로 사용하기](https://share.streamlit.io/)

## 🏠 로컬 실행

### 1. 저장소 클론
```bash
git clone https://github.com/rachael2222/prescription.git
cd prescription
```

### 2. 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env` 파일을 생성하고 다음과 같이 설정하세요:
```env
OPENAI_API_KEY=sk-your-openai-api-key
UPSTAGE_API_KEY=your-upstage-api-key
식약청_API_KEY=your-dur-api-key
식약청_API_BASE_URL=http://apis.data.go.kr/1471000/DURPrdlstInfoService03
```

### 5. 애플리케이션 실행
```bash
streamlit run medical_record_app.py
```

브라우저에서 `http://localhost:8501`로 접속하여 사용하세요!

## 🚀 Streamlit Community Cloud 배포

### 1. GitHub 저장소 준비
- 이 저장소를 fork하거나 clone
- 필요한 파일들이 모두 포함되어 있는지 확인:
  - `medical_record_app.py` (메인 앱)
  - `requirements.txt` (의존성)
  - `config.py` (설정)
  - 기타 필요한 Python 파일들

### 2. Streamlit Community Cloud 배포
1. [Streamlit Community Cloud](https://share.streamlit.io/) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 다음 정보 입력:
   - **Repository**: `rachael2222/prescription`
   - **Branch**: `main`
   - **Main file path**: `medical_record_app.py`

### 3. 환경 변수 설정
"Advanced settings" → "Secrets"에서 다음과 같이 설정:
```toml
[secrets]
OPENAI_API_KEY = ""
ocr_API_KEY = "your-upstage-key"
식약청_API_KEY = "your-dur-key"
식약청_API_BASE_URL = ""
```

### 4. 배포 완료
"Deploy!" 클릭하면 몇 분 후 온라인에서 사용 가능합니다!

## 📁 프로젝트 구조

```
prescription/
├── medical_record_app.py     # 메인 Streamlit 애플리케이션
├── config.py                 # API 키 및 설정 관리
├── medical_functions.py      # 의료 분석 관련 함수
├── dur_test_api.py          # DUR API 연동 함수
├── requirements.txt         # Python 의존성 패키지
├── .streamlit/             # Streamlit 설정 파일
├── samples/                # 샘플 처방전 이미지
├── prescription1.png       # 테스트용 처방전 이미지
├── prescription4.png       # 테스트용 처방전 이미지
└── README.md               # 이 파일
```

## 🔑 API 키 발급 방법

### OpenAI API
1. [OpenAI 플랫폼](https://platform.openai.com/api-keys) 접속
2. API 키 생성
3. 결제 방법 등록 (사용량 기반 과금)

### Upstage API  
1. [Upstage 콘솔](https://console.upstage.ai/) 접속
2. 회원가입 후 API 키 발급
3. OCR 서비스 활성화

### DUR API
1. [공공데이터포털](https://www.data.go.kr/) 접속
2. "DUR 품목정보 서비스" 검색
3. 활용 신청 후 API 키 발급

## 📋 사용 방법

1. **이미지 업로드**: 처방전 이미지를 업로드
2. **AI 분석**: 자동으로 텍스트 추출 및 약품 정보 분석
3. **결과 확인**: 약품명, 효능, 주의사항 등 확인
4. **음성 청취**: 결과를 음성으로 들어보기
5. **SMS 공유**: 필요시 모바일로 결과 전송

## 🔒 보안 및 개인정보

- 업로드된 이미지는 분석 후 즉시 삭제
- API 키는 환경 변수로 안전하게 관리
- 개인 의료정보는 저장되지 않음

## 📞 지원 및 문의

- **GitHub Issues**: [문제 신고](https://github.com/rachael2222/prescription/issues)
- **Feature Request**: 새로운 기능 제안 환영

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**⚠️ 중요 안내**

본 서비스는 **참고용**으로만 사용하시기 바랍니다. 

- 정확한 의료 정보는 반드시 **의료진과 상담**하세요
- AI 분석 결과는 100% 정확하지 않을 수 있습니다
- 약물 복용 전 반드시 **약사 또는 의사와 상의**하세요

**🏥 건강한 약물 복용을 위해 전문가의 조언을 구하시기 바랍니다!** 
