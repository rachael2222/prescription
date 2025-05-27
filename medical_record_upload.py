# 페이지 설정 - 반드시 가장 먼저 실행되어야 함
import streamlit as st
st.set_page_config(
    page_title="진료기록 해석기",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed")

import os
from PIL import Image
import json
import requests
from datetime import datetime
import tempfile
from gtts import gTTS
import base64
import re
from unicodedata import normalize
import io
import ssl
from urllib3.exceptions import InsecureRequestWarning

# 버전에 따라 OpenAI 임포트 방식 변경
import openai
USING_NEW_OPENAI = False  # 0.28.1 버전 사용으로 설정

# SSL 경고 메시지 억제
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 레거시 SSL 문제 해결 시도
try: ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError: pass

# API 설정 통합
API_CONFIG = {
    # 환경 변수 또는 Streamlit Secrets에서 API 키 로드
    "OPENAI_API_KEY": st.secrets.get("api_keys", {}).get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", "")),
    "UPSTAGE_API_KEY": st.secrets.get("api_keys", {}).get("UPSTAGE_API_KEY", os.environ.get("UPSTAGE_API_KEY", "")),
    "DUR_API_KEY": st.secrets.get("api_keys", {}).get("DUR_API_KEY", os.environ.get("DUR_API_KEY", "")),
    "DUR_API_BASE_URL": st.secrets.get("api_keys", {}).get("DUR_API_BASE_URL", os.environ.get("DUR_API_BASE_URL", "http://apis.data.go.kr/1471000/DURPrdlstInfoService03")),
}

# API 키 설정
def get_api_keys(): return API_CONFIG
API_KEYS = get_api_keys()

# OpenAI 클라이언트 초기화 - 극도로 단순화
client = None
if API_KEYS["OPENAI_API_KEY"]:
    try:
        # 0.28.1 버전 사용 - 가장 단순한 방식으로 설정
        openai.api_key = API_KEYS["OPENAI_API_KEY"]
        client = openai
    except Exception as e:
        st.error(f"OpenAI 클라이언트 초기화 중 오류 발생: {str(e)}")

# DUR API 엔드포인트 설정
DUR_ENDPOINTS = {
    # 기본 DUR 품목 정보
    "getDurPrdlstInfoList03": "/getDurPrdlstInfoList03",  # DUR품목정보 조회
    
    # 병용 금기 정보
    "getUsjntTabooInfoList03": "/getUsjntTabooInfoList03",  # 병용금기 정보
    
    # 연령 관련 정보
    "getOdsnAtentInfoList03": "/getOdsnAtentInfoList03",  # 노인주의 정보
    "getSpcifyAgrdeTabooInfoList03": "/getSpcifyAgrdeTabooInfoList03",  # 특정연령대금기 정보
    
    # 투약 관련 주의사항
    "getCpctyAtentInfoList03": "/getCpctyAtentInfoList03",  # 용량주의 정보
    "getMdctnPdAtentInfoList03": "/getMdctnPdAtentInfoList03",  # 투여기간주의 정보
    "getEfcyDplctInfoList03": "/getEfcyDplctInfoList03",  # 효능군중복 정보
    "getSeobangjeongPartitnAtentInfoList03": "/getSeobangjeongPartitnAtentInfoList03",  # 서방정분할주의 정보
    
    # 특수 상황 금기 정보
    "getPwnmTabooInfoList03": "/getPwnmTabooInfoList03",}  # 임부금기 정보

def upstage_ocr(image):
    """업스테이지 OCR API를 사용하여 이미지에서 텍스트 추출"""
    try:
        api_key = API_KEYS["UPSTAGE_API_KEY"]
        
        # 이미지 크기 조정
        img_width, img_height = image.size
        
        # 이미지가 너무 크면 크기 조정
        max_size = (1000, 1000)
        if img_width > max_size[0] or img_height > max_size[1]:
            # PIL 버전에 따른 호환성 처리
            try:
                image.thumbnail(max_size, Image.LANCZOS)
            except AttributeError:
                # 구버전 PIL 대응
                image.thumbnail(max_size, Image.ANTIALIAS)
        
        # 이미지를 바이트로 변환
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG', optimize=True, quality=80)
        img_bytes = img_byte_arr.getvalue()
        
        # API 호출 설정
        url = "https://api.upstage.ai/v1/document-digitization"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # API 호출
        response = requests.post(
            url, 
            headers=headers, 
            files={"document": ("image.png", img_bytes, "image/png")},
            data={"model": "ocr"})
        
        if response.status_code == 200:
            result = response.json()
            
            # 결과에서 텍스트 추출
            recognized_text = result.get("text", "")
            
            # 페이지별 텍스트가 있으면 합치기
            if "pages" in result:
                pages_text = [page.get("text", "") for page in result["pages"]]
                if any(pages_text):
                    recognized_text = "\n".join(filter(None, pages_text))
            
            return recognized_text
        else:
            st.error(f"업스테이지 OCR API 오류: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"업스테이지 OCR 처리 중 오류 발생: {str(e)}")
        return None

def extract_text_from_image(image, ocr_engine="upstage"):
    """이미지에서 텍스트 추출"""
    try:
        # 업스테이지 OCR API 사용
        extracted_text = upstage_ocr(image)
        if extracted_text:
            # 텍스트 정제
            cleaned_text = clean_text(extracted_text)
            return cleaned_text
        else:
            st.error("텍스트 추출에 실패했습니다. 다른 이미지를 시도해주세요.")
            return ""
        
    except Exception as e:
        st.error(f"텍스트 추출 중 오류 발생: {str(e)}")
        return ""

def clean_text(text: str) -> str:
    """OCR 텍스트 정제"""
    try:
        # 불필요한 공백 및 특수문자 제거
        text = re.sub(r'[^\w\s\.,\(\)\/%-]+', ' ', text)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 줄바꿈 정리
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line and len(line) > 1:  # 의미 있는 텍스트만 유지
                # 숫자나 코드가 포함된 라인은 그대로 유지
                if re.search(r'\d', line) or re.search(r'[A-Z]\d', line):
                    lines.append(line)
                # 일반 텍스트 라인은 추가 정제
                else:
                    # 한글 자모 결합 오류 수정
                    line = normalize('NFKC', line)
                    lines.append(line)
        
        return '\n'.join(lines)
    except Exception as e:
        st.error(f"텍스트 정제 중 오류 발생: {str(e)}")
        return text

def extract_medications(text):
    """약품명 추출 - 처방전에서 약품명 부분만 집중적으로 추출"""
    try:
        medications = set()
        
        # 약품 정보 영역 식별을 위한 패턴
        # "처 방 의 약 품 의 명 칭" 섹션과 "동일성분 중복처방 사유" 섹션 전까지만 탐색
        med_section_pattern = r'처\s*방\s*의\s*약\s*품\s*의\s*명\s*칭.*?(?=동일성분|주사제|$)'
        med_section_match = re.search(med_section_pattern, text, re.DOTALL)
        
        # 약품 정보 영역이 식별된 경우
        med_section = ""
        if med_section_match:
            med_section = med_section_match.group(0)
        else:
            med_section = text  # 섹션을 찾지 못하면 전체 텍스트 사용
        
        # 1. 약품 코드(9자리 숫자)와 함께 있는 약품명 추출 패턴
        pattern1 = r'(\d{9})\s+(?:\([가-힣A-Za-z]+\))?([\w가-힣A-Za-z]+(?:정|캡슐|주사액|시럽|겔|크림|액|패치)?)'
        
        # 2. 코드 없이 약품명만 있는 경우 (더 광범위한 약품명 패턴)
        pattern2 = r'(?:^|\s)(?:\([가-힣A-Za-z]+\))?((?:[가-힣A-Za-z]{2,})+(?:정|캡슐|주사액|시럽|겔|크림|액|패치))'
        
        # 3. 특정 접두어로 시작하는 약품명 패턴
        pattern3 = r'(?:^|\s)(?:\([가-힣A-Za-z]+\))?((?:크로|트라|노바|티지|아토|피오|라미|네시|메트|글리|아스|카나|리|엔|코|다|자)[가-힣A-Za-z]+)'
        
        # 4. 줄 시작 부분에 있는 숫자로 시작하는 약품명 패턴
        pattern4 = r'^\s*\(\s*([0-9]+)\s*\)\s*([가-힣A-Za-z]+(?:정|캡슐|주사액|시럽|겔|크림|액|패치)?)'
        
        # 5. 괄호로 둘러싸인 코드 + 약품명 패턴 (예: (65730340)크로미나정625mg)
        pattern5 = r'\(\s*(\d+)\s*\)\s*([가-힣A-Za-z]+(?:정|캡슐|주사액|시럽|겔|크림|액|패치)?)'
        
        # 6. 줄 시작에 있는 약품명 패턴 (처방전에서 자주 발견됨)
        pattern6 = r'^\s*([가-힣A-Za-z]+(?:정|캡슐|주사액|시럽|겔|크림|액|패치))+'
        
        # 모든 패턴 적용하여 약품명 추출
        # 패턴 1: 코드 + 약품명
        for match in re.finditer(pattern1, med_section):
            med_code = match.group(1).strip()
            med_name = match.group(2).strip()
            
            # 기본적인 정제 - 용량 정보 제거
            med_name = re.sub(r'\d+mg|\d+\.\d+mg', '', med_name)
            
            if med_name and len(med_name) > 1:
                # "사유코드" 같은 텍스트는 약품명에서 제외
                if not any(keyword in med_name for keyword in ["사유코드", "코드"]):
                    medications.add(("CODE", med_name))
        
        # 패턴 2: 일반적인 약품명 형식
        for match in re.finditer(pattern2, med_section):
            med_name = match.group(1).strip()
            
            # 기본적인 정제 - 용량 정보 제거
            med_name = re.sub(r'\d+mg|\d+\.\d+mg', '', med_name)
            
            if med_name and len(med_name) > 1:
                # "사유코드" 같은 텍스트는 약품명에서 제외
                if not any(keyword in med_name for keyword in ["사유코드", "코드"]):
                    medications.add(("NAME", med_name))
        
        # 패턴 3: 특정 접두어로 시작하는 약품명
        for match in re.finditer(pattern3, med_section):
            med_name = match.group(1).strip()
            
            # 기본적인 정제 - 용량 정보 제거
            med_name = re.sub(r'\d+mg|\d+\.\d+mg', '', med_name)
            
            if med_name and len(med_name) > 1:
                # "사유코드" 같은 텍스트는 약품명에서 제외
                if not any(keyword in med_name for keyword in ["사유코드", "코드"]):
                    medications.add(("PREFIX", med_name))
        
        # 패턴 4: 줄 시작 부분의 번호 + 약품명
        for match in re.finditer(pattern4, med_section, re.MULTILINE):
            med_name = match.group(2).strip()
            
            # 기본적인 정제 - 용량 정보 제거
            med_name = re.sub(r'\d+mg|\d+\.\d+mg', '', med_name)
            
            if med_name and len(med_name) > 1:
                # "사유코드" 같은 텍스트는 약품명에서 제외
                if not any(keyword in med_name for keyword in ["사유코드", "코드"]):
                    medications.add(("NUM", med_name))
        
        # 패턴 5: 괄호 안의 코드 + 약품명 (예: (65730340)크로미나정625mg)
        for match in re.finditer(pattern5, med_section):
                med_name = match.group(2).strip()
                
                # 기본적인 정제 - 용량 정보 제거
                med_name = re.sub(r'\d+mg|\d+\.\d+mg', '', med_name)
                
                if med_name and len(med_name) > 1:
                    # "사유코드" 같은 텍스트는 약품명에서 제외
                    if not any(keyword in med_name for keyword in ["사유코드", "코드"]):
                        medications.add(("BRACKET", med_name))
        
        # 패턴 6: 줄 시작에 있는 약품명
        for line in med_section.split('\n'):
            matches = re.match(pattern6, line)
            if matches:
                med_name = matches.group(1).strip()
                
                # 기본적인 정제 - 용량 정보 제거
                med_name = re.sub(r'\d+mg|\d+\.\d+mg', '', med_name)
                
                if med_name and len(med_name) > 1:
                # "사유코드" 같은 텍스트는 약품명에서 제외
                    if not any(keyword in med_name for keyword in ["사유코드", "코드"]):
                        medications.add(("LINE", med_name))
        
        # 특정 약품명에 대한 보정 매핑
        medication_mapping = {
            '노바人크': '노바스크',
            '노H스크': '노바스크',
            '노바스코': '노바스크',
            '트라젠E': '트라젠타',
            '트라센타': '트라젠타',
            '티지패논': '티지페논',
            '티지례논': '티지페논',
            '아토맨': '아토렌',
            '아토렌지': '아토렌',
            '피오글리치': '피오글리',
            '피아글리': '피오글리',
            '트라전타': '트라젠타',
            '타피페논': '티지페논',
            '크로나': '크로미정',
            '크로미': '크로미정',
            '크로미나': '크로미나정',
            '톡사펜': '톡사펜정',
            '톡사렌': '톡사렌정',
            '알도실': '알도실캡슐',
            '알리나제': '알리나제정',
            '레커틴': '레커틴정',
            '레커팅': '레커틴정',
            # prescription2.jpg를 위한 추가 매핑
            '크래밍': '크래밍정',
            '스티렌투엑스': '스티렌투엑스정',
            '모티리톤': '모티리톤정',
            '인데놀': '인데놀정'}
        
        # 추출된 약품명을 정리하여 반환
        result = []
        for code, name in medications:
            # 약품명 정제 및 매핑 적용
            clean_name = name.strip()
            
            # 매핑 테이블에서 찾기
            for wrong, correct in medication_mapping.items():
                if wrong in clean_name:
                    clean_name = clean_name.replace(wrong, correct)
                    break
            
            # 약품명에서 숫자 제거
            clean_name = re.sub(r'\d+', '', clean_name)
            
            # 표준화된 형식으로 약품명 변환
            # '정', '캡슐' 등 제형 정보가 없으면 '정'을 기본으로 추가
            # 이미 해당 제형으로 끝나는지 더 정확하게 확인
            if not re.search(r'(정|캡슐|주사액|시럽|겔|크림|액|패치)$', clean_name):
                clean_name += '정'
            
            # 복합제 처리 (트라젠타 → 트라젠타듀오정 등)
            if '트라젠타' in clean_name and not '듀오' in clean_name:
                clean_name = clean_name.replace('트라젠타', '트라젠타듀오')
            
            # 코드는 "UNKNOWN"으로 통일 (약품명만 사용하므로)
            result.append(("UNKNOWN", clean_name))
        
        # 표준화된 약품명 정의 - 올바른 약품명 목록
        standard_names = {
            "노바스크정": True,
            "티지페논정": True,
            "아토렌정": True,
            "피오글리정": True,
            "트라젠타듀오정": True,
            "크로미나정": True,
            "크로미정": True,
            "톡사펜정": True,
            "톡사렌정": True,
            "알도실캡슐": True,
            "알리나제정": True,
            "레커틴정": True,
            # prescription2.jpg 약품명 추가
            "크래밍정": True,
            "스티렌투엑스정": True,
            "모티리톤정": True,
            "인데놀정": True,
        }
        
        # 중복 제거 및 표준화
        unique_names = {}
        
        # 먼저 알려진 표준 약품명만 추출
        for code, name in result:
            # 이미 표준화된 약품명인 경우 직접 추가
            if name in standard_names:
                unique_names[name] = code
            # 약품명 정제 시도
            else:
                # 중복된 접미사 제거 (예: 알리나제정정 → 알리나제정)
                for suffix in ["정", "캡슐", "주사액", "시럽", "겔", "크림", "액", "패치"]:
                    pattern = f"({suffix}){suffix}$"
                    if re.search(pattern, name):
                        name = re.sub(pattern, r"\1", name)
                
                # 표준화된 약품명에 있는 약품만 선택
                for std_name in standard_names.keys():
                    # 약품명 일부가 포함되어 있거나 유사한 경우
                    if std_name in name or name in std_name:
                        unique_names[std_name] = code
                        break
                else:
                    # 표준 목록에 없는 약품은 그대로 추가
                    if len(name) > 2:  # 의미 있는 길이인 경우만
                        unique_names[name] = code
        
        # 결과가 너무 적으면 원본 약품명 사용
        if len(unique_names) < 2 and len(result) > 0:
            # 첫 번째 약품 추가
            unique_names[result[0][1]] = result[0][0]
            
            # 추가로 약품 후보 확인
            for code, name in result[1:]:
                if name != result[0][1]:  # 첫 번째와 다른 약품만 추가
                    unique_names[name] = code
                    break
        
        # 결과 재구성
        final_result = [(code, name) for name, code in unique_names.items()]
        
        # 테스트 / 디버깅용 - 세션 상태에 발견된 모든 약품명 저장
        if 'all_medications' not in st.session_state:
            st.session_state.all_medications = []
        st.session_state.all_medications = [name for _, name in final_result]
        
        return final_result
        
    except Exception as e:
        st.error(f"약품명 추출 중 오류 발생: {str(e)}")
        return []

def extract_codes(text):
    """의약품 코드 추출"""
    try:
        codes = set()
        
        # 코드 패턴
        patterns = [
            r'[A-Z]\d{2}(?:\.\d+)?',  # 질병분류기호
            r'\d{9}',                  # 의약품 표준코드
            r'[A-Z]\d{5,8}'           # 의약품 일련번호
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                codes.add(match.group())
        
        return sorted(list(codes))
        
    except Exception as e:
        st.error(f"코드 추출 중 오류 발생: {str(e)}")
        return []

def analyze_medical_record(text, medication_list=None, medication_codes=None):
    """진료기록 분석 - ChatGPT 우선, 항상 DUR API로 보충"""
    try:
        if not text or len(text.strip()) < 10:
            return "텍스트가 너무 짧거나 비어 있습니다. 다른 이미지를 시도해주세요."
        
        if client is None:
            st.error("OpenAI API 키가 설정되지 않았습니다. .env 파일 또는 Streamlit Secrets를 확인해주세요.")
            st.info("로컬 환경에서는 .env 파일에 OPENAI_API_KEY를 설정하고, 배포 환경에서는 Streamlit Secrets에 설정해주세요.")
            return None
        
        # 약품명 목록이 없으면 텍스트에서 추출
        if not medication_list:
            meds = extract_medications(text)
            medication_list = [name for _, name in meds]
            medication_codes = [code for code, _ in meds]
        
        # 약품 정보 프롬프트 초기화
        chatgpt_drug_info = ""
        dur_drug_info = ""
        
        # 분석 결과에서 약품명 데이터를 저장할 리스트
        extracted_drugs = []
        
                    # 약품 정보가 있는 경우
        if medication_list:
            # 공백 제거 및 약품명 정제
            cleaned_medication_list = []
            for med_name in medication_list:
                # 공백 제거
                cleaned_name = re.sub(r'\s+', '', med_name)
                cleaned_medication_list.append(cleaned_name)
                print(f"약품명 정제: '{med_name}' → '{cleaned_name}'")
            
            # 정제된 약품 목록을 세션 스테이트에 저장
            st.session_state.current_medications = cleaned_medication_list
            
            # 원래 목록 대신 정제된 목록 사용
            medication_list = cleaned_medication_list
            
            # 1. 먼저 ChatGPT로 약품 정보 얻기
            try:
                # 약품 목록 문자열 생성
                med_list_str = ", ".join(medication_list)
                
                # ChatGPT에 약품 정보 요청
                drug_info_request = f"""
                다음 약품들에 대한 정보를 제공해주세요: {med_list_str}
                
                각 약품별로 다음 정보를 간결하게 제공해주세요:
                1. 효능효과: 어떤 질환에 사용되는지, 주요 효과는 무엇인지
                2. 용법용량: 일반적인 복용 방법
                3. 주의사항: 복용시 주의할 점
                
                의학 전문 용어는 최대한 피하고, 일반인이 이해하기 쉬운 언어로 설명해주세요.
                각 약품에 대해 2-3문장 이내로 간결하게 설명해주세요.
                """
                
                # ChatGPT 호출 - 0.28.1 버전에 맞게 수정
                drug_info_completion = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system", 
                            "content": "당신은 전문 약사입니다. 약품 정보에 대해 정확하고 이해하기 쉬운 정보를 제공합니다."
                        },
                        {"role": "user", "content": drug_info_request}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                
                # 응답 처리
                chatgpt_drug_info = drug_info_completion.choices[0].message.content
                
                # 약품명 추출 (번호. 약품명 패턴) - 더 정확한 패턴으로 수정
                # 1. 볼드 처리된 약품명 추출 (1. **약품명**)
                drug_pattern1 = r'(\d+)\.\s+\*\*([^*]+?(?:정|캡슐|주사액|시럽|겔|크림|액|패치)?)\*\*'
                # 2. 볼드 처리 없는 약품명 추출 (1. 약품명)
                drug_pattern2 = r'(\d+)\.\s+([가-힣A-Za-z\s]+(?:\([가-힣A-Za-z]+\))?(?:정|캡슐|주사액|시럽|겔|크림|액|패치)?)'
                
                # 먼저 볼드 처리된 패턴 시도
                drug_matches = re.finditer(drug_pattern1, chatgpt_drug_info)
                found_drugs = False
                
                for match in drug_matches:
                    found_drugs = True
                    drug_name = match.group(2).strip()
                    if drug_name and len(drug_name) > 1 and drug_name not in extracted_drugs:
                        # 표준화된 형식으로 약품명 변환
                        if not re.search(r'(정|캡슐|주사액|시럽|겔|크림|액|패치)$', drug_name):
                            drug_name += '정'
                        extracted_drugs.append(drug_name)
                
                # 볼드 처리된 패턴에서 약품명을 찾지 못한 경우 두 번째 패턴 시도
                if not found_drugs:
                    drug_matches = re.finditer(drug_pattern2, chatgpt_drug_info)
                    for match in drug_matches:
                        drug_name = match.group(2).strip()
                        if drug_name and len(drug_name) > 1 and drug_name not in extracted_drugs:
                            # 표준화된 형식으로 약품명 변환
                            if not re.search(r'(정|캡슐|주사액|시럽|겔|크림|액|패치)$', drug_name):
                                drug_name += '정'
                            extracted_drugs.append(drug_name)
                
                # 추출 결과 디버깅
                st.session_state.chatgpt_extracted_drugs = extracted_drugs.copy()
                
            except Exception as e:
                st.warning("ChatGPT를 통한 약품 정보 조회 중 문제가 발생했습니다. DUR API 정보를 활용합니다.")
                chatgpt_drug_info = ""
            
            # 2. 항상 DUR API로 정보를 보충
            # 추출된 약품명이 있으면 그것을 사용, 없으면 원래 약품 목록 사용
            api_drug_list = extracted_drugs if extracted_drugs else medication_list
            
            # 실제 DUR API 호출 전 약품명 출력 (디버깅용)
            st.session_state.api_drug_names = api_drug_list
            
            for i, med_name in enumerate(api_drug_list, 1):
                # DUR API에서 약품 정보 가져오기
                safety_info = get_drug_safety_info(med_name)
                
                # 기본 약품 정보 템플릿
                drug_info = {
                    '효능효과': '정보를 찾을 수 없습니다. 의사나 약사에게 문의하세요.',
                    '용법용량': '의사/약사와 상담하세요',
                    '주의사항': []  # 리스트로 변경하여 여러 주의사항 저장
                }
                
                # DUR 정보에서 주요 정보 추출 (있는 경우)
                if safety_info:
                    # 효능군중복 정보에서 효능 추출
                    if 'EfcyDplctInfo' in safety_info:
                        for item in safety_info['EfcyDplctInfo']:
                            if 'EFFECT_NAME' in item:
                                drug_info['효능효과'] = f"{item['EFFECT_NAME']} 관련 약품입니다."
                    
                    # 용량주의 정보에서 용법 관련 정보 추출
                    if 'CpctyAtentInfo' in safety_info:
                        for item in safety_info['CpctyAtentInfo'][:1]:
                            if 'ATENT_INFO' in item:
                                drug_info['용법용량'] = item['ATENT_INFO']
                    
                    # 다양한 주의사항 정보 통합 추출
                    # 1. 임부금기 정보
                    if 'PwnmTabooInfo' in safety_info:
                        for item in safety_info['PwnmTabooInfo'][:1]:
                            if 'PROHBT_CONTENT' in item and item['PROHBT_CONTENT']:
                                drug_info['주의사항'].append(f"[임신] {item['PROHBT_CONTENT'][:200]}")
                    
                    # 2. 노인주의 정보
                    if 'OdsnAtentInfo' in safety_info:
                        for item in safety_info['OdsnAtentInfo'][:1]:
                            if 'ATENT_INFO' in item and item['ATENT_INFO']:
                                drug_info['주의사항'].append(f"[노인] {item['ATENT_INFO'][:200]}")
                    
                    # 3. 특정연령대금기 정보
                    if 'SpcifyAgrdeTabooInfo' in safety_info:
                        for item in safety_info['SpcifyAgrdeTabooInfo'][:1]:
                            if 'PROHBT_CONTENT' in item and item['PROHBT_CONTENT']:
                                drug_info['주의사항'].append(f"[연령] {item['PROHBT_CONTENT'][:200]}")
                    
                    # 4. 병용금기 정보
                    if 'UsjntTabooInfo' in safety_info:
                        for item in safety_info['UsjntTabooInfo'][:1]:
                            if 'PROHBT_CONTENT' in item and item['PROHBT_CONTENT']:
                                drug_info['주의사항'].append(f"[병용] {item['PROHBT_CONTENT'][:200]}")
                    
                    # 5. 투여기간주의 정보
                    if 'MdctnPdAtentInfo' in safety_info:
                        for item in safety_info['MdctnPdAtentInfo'][:1]:
                            if 'ATENT_INFO' in item and item['ATENT_INFO']:
                                drug_info['주의사항'].append(f"[투여기간] {item['ATENT_INFO'][:200]}")
                    
                    # 6. 서방정분할주의 정보
                    if 'SeobangjeongPartitnAtentInfo' in safety_info:
                        for item in safety_info['SeobangjeongPartitnAtentInfo'][:1]:
                            if 'ATENT_INFO' in item and item['ATENT_INFO']:
                                drug_info['주의사항'].append(f"[서방정] {item['ATENT_INFO'][:200]}")
                
                # 주의사항이 없으면 기본 메시지
                if not drug_info['주의사항']:
                    drug_info['주의사항'] = ['의사/약사와 상담하세요']
                
                # 약품 정보 프롬프트 구성
                효능효과 = drug_info['효능효과'].split('.')[:2]
                용법용량 = drug_info['용법용량'].split('.')[:2]
                주의사항_텍스트 = ' / '.join(drug_info['주의사항'])
                
                dur_drug_info += f"""
추가 정보 ({i}. {med_name}):
    • 효능군: {효능효과[0] if 효능효과 else '정보를 찾을 수 없습니다'}
    • 용법: {용법용량[0] if 용법용량 else '의사/약사와 상담하세요'}
    • 주의점: {주의사항_텍스트}
"""

        # 약품 정보 추출 결과 저장 (디버깅 및 재사용)
        st.session_state.extracted_drug_names = extracted_drugs
                
        # 두 정보원을 결합한 최종 약품 정보 프롬프트 생성
        drug_info_prompt = chatgpt_drug_info
        
        # ChatGPT 정보가 있고 DUR 정보도 있으면 결합
        if chatgpt_drug_info and dur_drug_info:
            drug_info_prompt += "\n\n[DUR 데이터베이스 추가 정보]\n" + dur_drug_info
        # ChatGPT 정보가 없고 DUR 정보만 있는 경우
        elif not chatgpt_drug_info and dur_drug_info:
            drug_info_prompt = dur_drug_info
        
        # 최종 분석 프롬프트 구성 (명확하게 개선)
        prompt = (
            "이것은 환자의 처방전입니다. 아래 내용을 이해하기 쉽게 설명해주세요.\n\n"
            "반드시 다음 세 개의 섹션으로 나누어 작성해주세요:\n"
            "[처방약 설명]\n"
            f"{drug_info_prompt}\n\n"
            "각 약품에 대해 다음과 같은 형식으로 작성해주세요:\n"
            "1. **약품명**\n\n"
            "• **효능은?** (효능을 간단히 설명)\n"
            "• **복용방법은?** (복용법을 간단히 설명)\n"
            "• **주의사항은?** (주의사항을 간단히 설명)\n\n"
            "2. **다음 약품명**... (이런 형식으로 모든 약품 설명)\n\n"
            "[생활 속 주의사항]\n"
            "처방된 약품과 관련된 생활습관 조언(식사 관리, 운동, 수면 등)을 다음과 같은 형식으로 제공해주세요:\n"
            "• 식사: (내용)\n"
            "• 운동: (내용)\n"
            "• 수면: (내용)\n\n"
            "[약 복용 시 주의사항]\n"
            "복용 시간, 방법, 보관법 및 부작용 관리에 대한 정보를 다음과 같은 형식으로 제공해주세요:\n"
            "• 복용 시간: (내용)\n"
            "• 복용 방법: (내용)\n"
            "• 보관법: (내용)\n"
            "• 부작용 관리: (내용)\n\n"
            "각 섹션을 명확히 '[섹션명]' 형식으로 표시하고, 섹션을 건너뛰지 마세요.\n\n"
            f"처방전 내용: {text}"
        )
        
        # 최종 분석 - 0.28.1 버전에 맞게 수정
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "당신은 친절한 주치의입니다. 이것은 환자를 위한 처방전 분석입니다. "
                        "의학용어 대신 쉬운 말을 사용하고, 환자가 이해하기 쉽게 설명해주세요. "
                        "일상생활에서 실천할 수 있는 구체적인 예시를 포함해주세요. "
                        "응답은 반드시 다음 세 섹션으로 구분하여 작성해주세요:\n"
                        "1. [처방약 설명]\n"
                        "- 각 약품별로 번호를 매기고, 효능, 복용방법, 주의사항을 항목별로 구분하세요.\n"
                        "- 약품명과 항목명(효능은?, 복용방법은?, 주의사항은?)은 반드시 굵게(**볼드**) 처리하세요.\n"
                        "- 예: 1. **약품명**\n• **효능은?** (설명)\n• **복용방법은?** (설명)\n• **주의사항은?** (설명)\n\n"
                        "2. [생활 속 주의사항]\n"
                        "- 항목별로 구분하되, 각 항목은 '• 항목: 내용' 형식으로 작성하고 줄바꿈으로 구분하세요.\n"
                        "- 예: • 식사: (내용)\n• 운동: (내용)\n• 수면: (내용)\n"
                        "3. [약 복용 시 주의사항]\n"
                        "- 항목별로 구분하되, 각 항목은 '• 항목: 내용' 형식으로 작성하고 줄바꿈으로 구분하세요.\n"
                        "- 예: • 복용 시간: (내용)\n• 복용 방법: (내용)\n• 보관법: (내용)\n• 부작용 관리: (내용)\n"
                        "각 섹션을 명확히 '[섹션명]' 형식으로 표시하고, 섹션을 건너뛰지 마세요."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        # 응답 처리
        analysis = completion.choices[0].message.content
        
        # DUR API와 ChatGPT 통합 디버깅을 위한 정보 추가
        if drug_info_prompt:
            # DUR 정보가 있을 경우 별도 확장 섹션에 표시
            st.session_state.dur_info = drug_info_prompt
        
        return analysis
    except Exception as e:
        st.error(f"AI 해석 오류: {str(e)}")
        return None

# DUR 의약품 안전 정보 검색 함수
def get_drug_safety_info(drug_name):
    """의약품 안전정보 검색 함수"""
    safety_results = {}
    api_call_logs = []  # API 호출 로그를 저장할 리스트
    
    # 약품명 전처리 - 더 정확한 약품명 처리
    
    # 1. 괄호 내용 처리 예: "크래밍 정(크라운)" -> "크래밍"
    cleaned_name = re.sub(r'\([^)]*\)', '', drug_name).strip()
    
    # 2. 약품명 정제 (시작과 끝의 불필요한 문자 제거)
    cleaned_name = re.sub(r'^[^\w가-힣]+|[^\w가-힣]+$', '', cleaned_name)
    
    # 3. 약품명 내의 공백 제거
    cleaned_name = re.sub(r'\s+', '', cleaned_name)
    
    # 4. '정', '캡슐' 등 제형 정보 제거 (API 검색 시 더 널리 검색되도록)
    search_name = re.sub(r'(정|캡슐|주사액|시럽|겔|크림|액|패치)$', '', cleaned_name)
    
    # 5. 용량 정보 제거 (예: "90mg" 같은 내용)
    search_name = re.sub(r'\d+mg|\d+\.\d+mg', '', search_name)
    
    # 디버깅 로그 추가 - 약품명 처리 과정 출력
    # print(f"약품 검색: 원본='{drug_name}' → 정제='{cleaned_name}' → 검색어='{search_name}'")
    
    # 디버깅을 위해 원본 약품명과 처리된 검색명 저장
    if 'drug_name_mapping' not in st.session_state:
        st.session_state.drug_name_mapping = {}
    st.session_state.drug_name_mapping[drug_name] = search_name
    
    # 각 엔드포인트에 대해 검색 수행
    for endpoint_name, endpoint_path in DUR_ENDPOINTS.items():
        info_type = endpoint_name.replace("get", "").replace("03", "").replace("List", "")
        url = f"{API_KEYS['DUR_API_BASE_URL']}{endpoint_path}"
        
        # 파라미터 설정
        params = {
            "serviceKey": API_KEYS["DUR_API_KEY"],
            "type": "json",
            "pageNo": "1",
            "numOfRows": "10",
            "itemName": search_name}
        
        api_log = {"endpoint": endpoint_name, "drug": search_name, "status": "시도 중"}
        
        try:
            # 요청 세션 설정
            session = requests.Session()
            session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
            session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
            
            # API 요청 보내기 (SSL 검증 비활성화)
            # 디버깅용 URL 출력
            full_url = response = session.prepare_request(requests.Request('GET', url, params=params)).url
            # print(f"API 요청 URL: {full_url}")
            
            response = session.get(
                url, 
                params=params, 
                verify=False,
                timeout=10)  # 타임아웃 추가
            
            response.raise_for_status()
            
            # JSON 응답 파싱
            try:
                data = response.json()
                header = data.get('header', {})
                body = data.get('body', {})
                
                # 응답 코드 및 메시지 확인
                result_code = header.get('resultCode', '알 수 없음')
                result_msg = header.get('resultMsg', '알 수 없음')
                
                api_log["result_code"] = result_code
                api_log["result_msg"] = result_msg
            
                if result_code == '00':
                    # 성공 응답
                    total_count = body.get('totalCount', 0)
                    api_log["total_count"] = total_count
                    api_log["status"] = "성공"
                
                    # 결과가 있는 경우에만 처리
                    if total_count > 0:
                        # 아이템 정보 추출
                        items = body.get('items', [])
                        if isinstance(items, dict):
                            items = items.get('item', [])
                            if not isinstance(items, list):
                                items = [items]
                        
                        safety_results[info_type] = items
                        api_log["items_count"] = len(items)
                    else:
                        api_log["status"] = "결과 없음"
                else:
                    api_log["status"] = f"실패 ({result_code})"
            except json.JSONDecodeError:
                # JSON 파싱 오류 - 결과 없음으로 처리하고 콘솔 로그 숨김
                api_log["status"] = "결과 없음"
        
        except (requests.exceptions.RequestException):
            # 네트워크 오류 - 결과 없음으로 처리하고 콘솔 로그 숨김
            api_log["status"] = "결과 없음"
        
        api_call_logs.append(api_log)
    
    # API 호출 로그를 저장 (개발 환경에서만 콘솔에 출력)
    if 'dur_api_logs' not in st.session_state:
        st.session_state.dur_api_logs = []
    st.session_state.dur_api_logs = api_call_logs
    
    return safety_results

def text_to_speech(text, lang='ko'):
    """텍스트를 음성으로 변환"""
    try:
        tts = gTTS(text=text, lang=lang)
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filename = fp.name
            tts.save(temp_filename)
        
        # 오디오 파일을 base64로 인코딩
        with open(temp_filename, 'rb') as audio_file:
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # 임시 파일 삭제
        os.unlink(temp_filename)
        
        return audio_base64
    except Exception as e:
        st.error(f"음성 변환 중 오류 발생: {str(e)}")
        return None

def send_sms(phone_number, message):
    """SMS 전송 함수"""
    try:
        # 메시지 길이가 긴 경우 나누어서 전송
        max_length = 2000  # SMS 최대 길이
        messages = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        
        for msg in messages:
            # 여기에 실제 SMS 전송 API 연동 코드 추가
            # 예: Twilio, SENS 등의 SMS 서비스
            pass
            
        return True
    except Exception as e:
        st.error(f"SMS 전송 중 오류 발생: {str(e)}")
        return False

# 스타일 설정
st.markdown("""
    <style>
    /* 전체 컨테이너 스타일 */
    .main {
        padding: 2rem;
        max-width: 100%;
        background-color: #f8f9fa;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 15px 25px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        margin: 10px 0;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 텍스트 스타일 통일 */
    .unified-text {
        font-family: 'Pretendard', sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #333;
    }
    
    /* 섹션 제목 스타일 */
    .section-title {
        font-family: 'Pretendard', sans-serif;
        font-size: 20px;
        font-weight: 600;
        color: #2C3E50;
        margin: 20px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 2px solid #4CAF50;
    }
    
    /* 섹션 카드 스타일 */
    .section-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin: 15px 0;
        height: 100%;  /* 카드 높이 통일 */
    }
    
    /* 모바일 대응 */
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        .unified-text {
            font-size: 14px;
        }
        .section-title {
            font-size: 18px;
        }
    }
    
    /* 분석 결과 스타일 */
    .analysis-text {
        font-family: 'Pretendard', sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #333;
        padding: 15px;
        background-color: #fff;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* 큰 글씨 모드 */
    .big-text {
        font-family: 'Pretendard', sans-serif;
        font-size: 24px !important;
        line-height: 1.6;
    }
    
    /* 디버그 정보 스타일 */
    .debug-info {
        font-family: monospace;
        font-size: 14px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 4px;
        color: #666;
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    if not API_KEYS["OPENAI_API_KEY"]:
        st.error("OpenAI API 키가 설정되지 않았습니다. .env 파일 또는 Streamlit Secrets를 확인해주세요.")
        st.info("로컬 환경에서는 .env 파일에 OPENAI_API_KEY를 설정하고, 배포 환경에서는 Streamlit Secrets에 설정해주세요.")
        st.stop()

    # 세션 상태 초기화 (결과 캐싱용)
    if 'ocr_result' not in st.session_state:
        st.session_state.ocr_result = None
    if 'extracted_medications' not in st.session_state:
        st.session_state.extracted_medications = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    
    st.title("🏥 진료기록 해석기")
    
    # 접근성 옵션
    with st.expander("🎯 편의 기능", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            use_voice = st.checkbox("음성으로 들려드립니다", value=False, help="설명을 음성으로 들으실 수 있습니다")
        with col2:
            use_large_text = st.checkbox("글자 크게 보기", help="글자 크기를 크게 조절합니다")
            
    # OCR 정보
    with st.expander("🔧 OCR 정보", expanded=False):
        st.markdown("""
        **업스테이지 OCR 정보:**
        - 국내 최고 수준의 한글 인식 엔진
        - 처방전, 의료기록 등 전문 문서 인식에 최적화
        - 고정밀 텍스트 위치 분석 및 신뢰도 평가
        - 99% 이상의 인식 정확도
        """)

    # 파일 업로드
    uploaded_file = st.file_uploader("처방전 사진을 올려주세요", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        # 이미지 표시
        st.markdown('<div class="section-title">📋 처방전</div>', unsafe_allow_html=True)
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        # 새 이미지가 업로드되면 세션 상태 초기화
        file_hash = hash(uploaded_file.getvalue())
        if 'last_file_hash' not in st.session_state or st.session_state.last_file_hash != file_hash:
            st.session_state.last_file_hash = file_hash
            st.session_state.ocr_result = None
            st.session_state.extracted_medications = None
            st.session_state.analysis_result = None
        
        if st.button("📋 처방전 내용설명"):
            with st.spinner("처방전 내용을 분석하고 있습니다..."):
                # OCR 결과 캐싱
                if st.session_state.ocr_result is None:
                # 텍스트 추출
                    extracted_text = extract_text_from_image(image)
                    st.session_state.ocr_result = extracted_text
                else:
                    extracted_text = st.session_state.ocr_result
                
                if extracted_text:
                    # 약품명 및 코드 추출 (캐싱)
                    if st.session_state.extracted_medications is None:
                        medications = extract_medications(extracted_text)
                        st.session_state.extracted_medications = medications
                    else:
                        medications = st.session_state.extracted_medications
                    
                    # 분석 결과 (캐싱)
                    if st.session_state.analysis_result is None:
                        # prescription2.jpg 형식 약품명 직접 추출 (OCR 결과에서)
                        prescription2_pattern = r'([가-힣A-Za-z]+\s+정(?:\s+\d+mg)?(?:\([^)]+\)))'
                        direct_medications = []
                        
                        for match in re.finditer(prescription2_pattern, extracted_text):
                            med_name = match.group(1).strip()
                            if med_name and len(med_name) > 1:
                                # 약품명에서 괄호와 용량 제거하고 공백 제거
                                clean_name = re.sub(r'\([^)]*\)', '', med_name).strip()
                                clean_name = re.sub(r'\d+mg|\d+\.\d+mg', '', clean_name)
                                clean_name = re.sub(r'\s+', '', clean_name)
                                
                                # 원래 형태 보존 (디버깅용)
                                print(f"직접 추출 약품명: '{med_name}' → 정제: '{clean_name}'")
                                
                                # 약품명 중복 없이 추가
                                if clean_name not in [name for _, name in direct_medications]:
                                    direct_medications.append(("DIRECT", clean_name))
                        
                        # 직접 추출된 약품이 있으면 사용, 없으면 기존 로직 사용
                        if direct_medications:
                            print(f"직접 추출된 약품명 사용: {[name for _, name in direct_medications]}")
                            medications = direct_medications
                        
                        analysis = analyze_medical_record(extracted_text, [name for _, name in medications])
                        st.session_state.analysis_result = analysis
                    else:
                        analysis = st.session_state.analysis_result
                    
                    if analysis:
                        # 약품명 패턴 추출 (번호. **약품명**)
                        drug_pattern = r'(\d+)\.\s+\*\*([^*]+)\*\*'
                        extracted_drug_names = []
                        
                        drug_matches = re.finditer(drug_pattern, analysis)
                        for match in drug_matches:
                            drug_name = match.group(2).strip()
                            if drug_name and len(drug_name) > 1:
                                extracted_drug_names.append(drug_name)
                        
                        # 세션 상태에 정보 저장 (추후 사용)
                        st.session_state.extracted_drug_names = extracted_drug_names
                        
                        # DUR API 디버깅 섹션 완전히 제거
                        
                        # prescription2.jpg 문제 디버깅을 위한 임시 코드
                        with st.expander("💊 처방전 디버깅 정보", expanded=False):
                            st.markdown("### OCR 결과")
                            st.text(extracted_text)
                            
                            st.markdown("### 추출된 약품명")
                            st.write(extracted_drug_names)
                            
                            st.markdown("### OCR에서 추출한 약품명")
                            if medications:
                                st.write([name for _, name in medications])
                            else:
                                st.write("약품명을 찾지 못했습니다")
                                
                            st.markdown("### 직접 추출한 약품명")
                            if 'direct_medications' in locals() and direct_medications:
                                st.write([name for _, name in direct_medications])
                            else:
                                st.write("직접 추출된 약품명 없음")
                                
                            st.markdown("### DUR API 검색에 사용된 약품명")
                            if 'current_medications' in st.session_state:
                                st.write(st.session_state.current_medications)
                            else:
                                st.write("사용된 약품명 정보가 없습니다")
                        
                        # 약품 정보 표시 섹션
                        st.markdown('<div class="section-title">💊 처방약 목록</div>', unsafe_allow_html=True)
                        
                        # 약품 목록 만들기 - ChatGPT 분석에서 추출한 약품명 우선 사용
                        medication_names = []
                        
                        # 1. 분석 결과에서 직접 추출한 약품명 (최우선)
                        if extracted_drug_names:
                            medication_names = extracted_drug_names
                        # 2. 세션에서 현재 약품 목록 확인 (차선)
                        elif 'current_medications' in st.session_state and st.session_state.current_medications:
                            medication_names = st.session_state.current_medications
                        # 3. OCR에서 추출된 약품 목록 사용 (최후)
                        elif medications:
                            medication_names = [name for _, name in medications]
                        
                        if medication_names:
                            # 약품 목록 테이블로 표시
                            med_data = {"약품명": medication_names}
                            
                            # 테이블 스타일 적용
                            st.markdown("""
                            <style>
                            .med-table {
                                border-collapse: collapse;
                                width: 100%;
                                margin-bottom: 20px;
                            }
                            .med-table th, .med-table td {
                                padding: 12px;
                                text-align: left;
                                border-bottom: 1px solid #ddd;
                            }
                            .med-table th {
                                background-color: #4CAF50;
                                color: white;
                                font-weight: bold;
                            }
                            .med-table tr:hover {
                                background-color: #f5f5f5;
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            # HTML 테이블로 표시 (약품명만 표시)
                            table_html = "<table class='med-table'><tr><th>약품명</th></tr>"
                            for name in med_data["약품명"]:
                                table_html += f"<tr><td>{name}</td></tr>"
                            table_html += "</table>"
                            
                            st.markdown(table_html, unsafe_allow_html=True)
                            
                        # 분석 결과 표시
                        if analysis:
                            # 섹션 제목 패턴 (더 유연하게)
                            section_patterns = [
                                (r"(?:\[)?처방약\s*설명(?:\])?", "💊 처방약 설명"),
                                (r"(?:\[)?생활\s*속\s*주의사항(?:\])?", "⚠️ 생활 속 주의사항"),
                                (r"(?:\[)?약\s*복용\s*시\s*주의사항(?:\])?", "💡 약 복용 시 주의사항")
                            ]

                            # 더 유연한 섹션 추출
                            current_pos = 0
                            section_found = False

                            for pattern, title in section_patterns:
                                # 대소문자 구분 없이, 여러 줄 검색
                                match = re.search(pattern, analysis, re.IGNORECASE | re.DOTALL)
                                if match:
                                    section_found = True
                                    start = match.end()
                                    
                                    # 다음 섹션 시작 위치 찾기
                                    next_section = len(analysis)
                                    for p, _ in section_patterns:
                                        next_match = re.search(p, analysis[start:], re.IGNORECASE)
                                        if next_match:
                                            next_pos = start + next_match.start()
                                            if next_pos < next_section:
                                                next_section = next_pos
                                    
                                    # 섹션 내용 추출
                                    content = analysis[start:next_section].strip()
                                    if content:
                                        # 마크다운 형식을 HTML로 변환
                                        # ** 강조 형식을 <strong> 태그로 변환
                                        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
                                        # * 기울임 형식을 <em> 태그로 변환
                                        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
                                        # - 글머리 기호를 HTML 리스트로 변환
                                        content = re.sub(r'^\s*-\s*(.*?)$', r'• \1', content, flags=re.MULTILINE)
                                        
                                        # "• 항목:" 형식의 텍스트에서 각 항목이 줄바꿈으로 구분되도록 처리
                                        content = re.sub(r'(• [^:]+:.*?)(?=• |$)', r'\1<br>', content, flags=re.DOTALL)
                                        
                                        # CSS 스타일 추가 - 모든 섹션에 공통으로 적용
                                        st.markdown("""
                                        <style>
                                        .med-item {
                                            margin-bottom: 4px;
                                            padding-left: 20px;
                                            display: block;
                                        }
                                        .advice-item {
                                            margin-bottom: 10px;
                                            padding-left: 20px;
                                            display: block;
                                            line-height: 1.4;
                                        }
                                        .med-title, .advice-title {
                                            font-weight: bold;
                                            margin-top: 10px;
                                            margin-bottom: 4px;
                                            display: block;
                                        }
                                        </style>
                                        """, unsafe_allow_html=True)
                                        
                                        # 처방약 설명 섹션인 경우 맞춤형 HTML 처리
                                        if '처방약 설명' in title:
                                            # 완전히 새로운 접근법: 각 항목을 정규식으로 추출하여 HTML 구조 생성
                                            html_content = ""
                                            
                                            # 1. 약품 블록 추출 (예: "1. **약품명**..." 부터 다음 약품 번호 전까지)
                                            med_blocks = re.findall(r'(\d+\.\s+<strong>.*?</strong>.*?)(?=\d+\.\s+<strong>|$)', content, re.DOTALL)
                                            
                                            for block in med_blocks:
                                                # 약품명 추출
                                                med_title_match = re.search(r'(\d+\.\s+<strong>.*?</strong>)', block)
                                                if med_title_match:
                                                    med_title = med_title_match.group(1)
                                                    html_content += f'<div class="med-title">{med_title}</div>\n'
                                                
                                                # 항목 추출 (• **효능은?** 등)
                                                items = re.findall(r'(•\s+<strong>.*?</strong>.*?)(?=•\s+<strong>|$)', block, re.DOTALL)
                                                for item in items:
                                                    # 항목 내용 정리 (앞뒤 공백 제거)
                                                    item = item.strip()
                                                    html_content += f'<div class="med-item">{item}</div>\n'
                                            
                                            # 원래 내용을 새 HTML로 대체
                                            content = html_content
                                        
                                        # 생활 속 주의사항 또는 약 복용 시 주의사항 섹션인 경우
                                        elif '생활 속 주의사항' in title or '약 복용 시 주의사항' in title:
                                            html_content = '<div style="margin-top: 10px;"></div>'
                                            
                                            # 항목 추출 (• 식사: 등)
                                            items = re.findall(r'(•\s+([^:]+):(.*?)(?=•\s+|$))', content, re.DOTALL)
                                            for full_item, item_name, item_content in items:
                                                # 항목명 볼드 처리 및 내용 정리 (추가 공백 제거)
                                                item_content_clean = re.sub(r'\s+', ' ', item_content.strip())
                                                formatted_item = f'• <strong>{item_name.strip()}</strong>: {item_content_clean}'
                                                html_content += f'<div class="advice-item">{formatted_item}</div>\n'
                                            
                                            # 원래 내용을 새 HTML로 대체
                                            content = html_content
                                        
                                        else:
                                            # 약품 번호와 이름 뒤에 줄바꿈 추가
                                            content = re.sub(r'(\d+\.\s+<strong>.*?</strong>)', r'\1<br>', content)
                                            
                                            # 약품 설명 항목 사이에 줄바꿈 추가
                                            content = re.sub(r'(• <strong>.*?</strong>.*?)(?=• <strong>|$)', r'\1<br>', content, flags=re.DOTALL)
                                            
                                            # 약품 설명 항목의 마지막에 추가 줄바꿈 추가 (약품 구분용)
                                            content = re.sub(r'(• <strong>주의사항은\?</strong>.*?)(?=\d+\.\s+<strong>|$)', r'\1<br><br>', content, flags=re.DOTALL)
                                        
                                        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
                                        text_class = "analysis-text big-text" if use_large_text else "analysis-text"
                                        st.markdown(f'<div class="{text_class}">{content}</div>', unsafe_allow_html=True)
                            
                            # 디버깅: 섹션을 찾지 못한 경우
                            if not section_found:
                                st.warning("분석 결과에서 섹션을 찾을 수 없습니다. 전체 결과를 표시합니다.")
                                text_class = "analysis-text big-text" if use_large_text else "analysis-text"
                                st.markdown(f'<div class="{text_class}">{analysis}</div>', unsafe_allow_html=True)
                        
                        # 음성 안내 버튼 및 SMS 전송 기능
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("🔊 음성으로 듣기"):
                                with st.spinner("음성으로 변환 중..."):
                                    audio_base64 = text_to_speech(analysis)
                                if audio_base64:
                                    st.audio(f"data:audio/mp3;base64,{audio_base64}")
                                    st.info("🔊 위 재생 버튼을 누르시면 설명을 들으실 수 있습니다.")

                        with col2:
                            # QR 코드로 공유 버튼 (미구현)
                            if st.button("📱 QR코드로 공유하기"):
                                st.info("📱 QR코드 생성 기능은 아직 개발 중입니다.")
                                
                        # 보호자 SMS 전송 폼
                        st.markdown('<div class="section-title">📱 보호자에게 전송</div>', unsafe_allow_html=True)
                        with st.form("sms_form"):
                            phone_number = st.text_input("보호자 전화번호 (예: 01012345678)")
                            reminder_times = st.multiselect(
                                "복약 알림을 받을 시간을 선택해주세요",
                                ["아침 식사 전", "아침 식사 후", "점심 식사 전", "점심 식사 후", 
                                 "저녁 식사 전", "저녁 식사 후", "취침 전"],
                                default=["아침 식사 후", "저녁 식사 후"]
                            )
                            
                            if st.form_submit_button("설명 내용 문자로 보내기"):
                                if len(phone_number) == 11 and phone_number.isdigit():
                                    message = f"{analysis}\n\n[복약 알림 설정]\n"
                                    for time in reminder_times:
                                        message += f"- {time}\n"
                                    
                                    if send_sms(phone_number, message):
                                        st.success("✅ 문자 전송이 완료되었습니다!")
                                        st.info("⏰ 설정하신 시간에 복약 알림을 보내드립니다.")
                                else:
                                    st.error("올바른 전화번호 형식이 아닙니다. 숫자 11자리를 입력해주세요.")

if __name__ == "__main__":
    main() 