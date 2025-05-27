# 의료 기록 해석기

처방전을 분석하고 약품 정보를 제공하는 AI 기반 웹 애플리케이션입니다.

## 주요 기능

- 처방전 이미지 업로드 및 OCR 분석
- 약품명 자동 추출
- 약품 정보 및 주의사항 제공
- 생활 속 주의사항 안내
- 음성 안내 기능
- SMS 공유 기능

## 설치 및 실행 방법

### 로컬 환경에서 실행하기

1. 저장소 클론
```bash
git clone https://github.com/rachael2222/prescription.git
cd prescription
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 다음과 같이 API 키를 설정합니다:
```
OPENAI_API_KEY=your_openai_api_key_here
UPSTAGE_API_KEY=your_upstage_api_key_here
DUR_API_KEY=your_dur_api_key_here
DUR_API_BASE_URL=http://apis.data.go.kr/1471000/DURPrdlstInfoService03
```

**중요**: 실제 API 키를 입력하세요. 각 API 키는 다음에서 발급받을 수 있습니다:
- OpenAI API: https://platform.openai.com/api-keys
- Upstage API: https://console.upstage.ai/
- DUR API: https://www.data.go.kr/

5. 애플리케이션 실행
```bash
streamlit run medical_record_app.py
```

## Streamlit Cloud에 배포하기

1. [Streamlit Cloud](https://share.streamlit.io/)에 접속하고 GitHub 계정으로 로그인합니다.
2. 'New app' 버튼을 클릭합니다.
3. GitHub 저장소를 연결합니다.
4. 다음 설정을 구성합니다:
   - **Repository**: rachael2222/prescription
   - **Branch**: main
   - **Main file path**: medical_record_app.py
5. 'Advanced Settings'를 열고 'Secrets' 섹션에 API 키를 추가합니다:
   ```
   [api_keys]
   OPENAI_API_KEY = "실제_API_키_값"
   UPSTAGE_API_KEY = "실제_API_키_값" 
   DUR_API_KEY = "실제_API_키_값"
   DUR_API_BASE_URL = "http://apis.data.go.kr/1471000/DURPrdlstInfoService03"
   ```
6. 'Deploy!' 버튼을 클릭하여 배포를 시작합니다.

배포가 완료되면 Streamlit Cloud에서 제공하는 URL을 통해 애플리케이션에 접근할 수 있습니다.

## 기술 스택

- Streamlit: 웹 인터페이스
- OpenAI GPT-4o: 텍스트 분석 및 설명 생성
- Upstage OCR API: 이미지에서 텍스트 추출
- DUR API: 약품 안전 정보 조회
- gTTS: 텍스트-음성 변환 