import os
from PIL import Image
import openai
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

# SSL 경고 메시지 억제
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 레거시 SSL 문제 해결 시도
try: ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError: pass

# API 설정 - config.py에서 가져오기
from config import get_api_keys

# API 키 설정
API_KEYS = get_api_keys()

# OpenAI 클라이언트 초기화 (새 버전)
client = None
if API_KEYS["OPENAI_API_KEY"]:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=API_KEYS["OPENAI_API_KEY"])
    except Exception as e:
        print(f"OpenAI 클라이언트 초기화 중 오류 발생: {str(e)}")

# DUR API 엔드포인트 설정
DUR_ENDPOINTS = {
    "getDurPrdlstInfoList03": "/getDurPrdlstInfoList03",
    "getUsjntTabooInfoList03": "/getUsjntTabooInfoList03",
    "getOdsnAtentInfoList03": "/getOdsnAtentInfoList03",
    "getSpcifyAgrdeTabooInfoList03": "/getSpcifyAgrdeTabooInfoList03",
    "getCpctyAtentInfoList03": "/getCpctyAtentInfoList03",
    "getMdctnPdAtentInfoList03": "/getMdctnPdAtentInfoList03",
    "getEfcyDplctInfoList03": "/getEfcyDplctInfoList03",
    "getSeobangjeongPartitnAtentInfoList03": "/getSeobangjeongPartitnAtentInfoList03",
    "getPwnmTabooInfoList03": "/getPwnmTabooInfoList03",
}

def upstage_ocr(image):
    """업스테이지 OCR API를 사용하여 이미지에서 텍스트 추출"""
    try:
        api_key = API_KEYS["UPSTAGE_API_KEY"]
        
        # 이미지 크기 조정
        img_width, img_height = image.size
        
        # 이미지가 너무 크면 크기 조정
        max_size = (1000, 1000)
        if img_width > max_size[0] or img_height > max_size[1]:
            try:
                image.thumbnail(max_size, Image.LANCZOS)
            except AttributeError:
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
            print(f"업스테이지 OCR API 오류: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"업스테이지 OCR 처리 중 오류 발생: {str(e)}")
        return None

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
            if line and len(line) > 1:
                if re.search(r'\d', line) or re.search(r'[A-Z]\d', line):
                    lines.append(line)
                else:
                    line = normalize('NFKC', line)
                    lines.append(line)
        
        return '\n'.join(lines)
    except Exception as e:
        print(f"텍스트 정제 중 오류 발생: {str(e)}")
        return text

def extract_medications(text):
    """약품명 추출"""
    try:
        medications = set()
        
        # 약품 정보 영역 식별
        med_section_pattern = r'처\s*방\s*의\s*약\s*품\s*의\s*명\s*칭.*?(?=동일성분|주사제|$)'
        med_section_match = re.search(med_section_pattern, text, re.DOTALL)
        
        med_section = ""
        if med_section_match:
            med_section = med_section_match.group(0)
        else:
            med_section = text
        
        # 다양한 패턴으로 약품명 추출
        patterns = [
            r'(\d{9})\s+(?:\([가-힣A-Za-z]+\))?([\w가-힣A-Za-z]+(?:정|캡슐|주사액|시럽|겔|크림|액|패치)?)',
            r'(?:^|\s)(?:\([가-힣A-Za-z]+\))?((?:[가-힣A-Za-z]{2,})+(?:정|캡슐|주사액|시럽|겔|크림|액|패치))',
            r'\(\s*(\d+)\s*\)\s*([가-힣A-Za-z]+(?:정|캡슐|주사액|시럽|겔|크림|액|패치)?)'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, med_section):
                if len(match.groups()) >= 2:
                    med_name = match.group(2).strip()
                    med_name = re.sub(r'\d+mg|\d+\.\d+mg', '', med_name)
                    
                    if med_name and len(med_name) > 1:
                        if not any(keyword in med_name for keyword in ["사유코드", "코드"]):
                            medications.add(("EXTRACTED", med_name))
        
        # 약품명 정제 및 표준화
        medication_mapping = {
            '노바人크': '노바스크', '노H스크': '노바스크', '노바스코': '노바스크',
            '트라젠E': '트라젠타', '트라센타': '트라젠타', '트라전타': '트라젠타',
            '티지패논': '티지페논', '티지례논': '티지페논', '타피페논': '티지페논',
            '아토맨': '아토렌', '아토렌지': '아토렌',
            '피오글리치': '피오글리', '피아글리': '피오글리',
            '크로나': '크로미정', '크로미': '크로미정', '크로미나': '크로미나정',
            '크래밍': '크래밍정', '스티렌투엑스': '스티렌투엑스정',
            '모티리톤': '모티리톤정', '인데놀': '인데놀정'
        }
        
        result = []
        for code, name in medications:
            clean_name = name.strip()
            
            # 매핑 테이블 적용
            for wrong, correct in medication_mapping.items():
                if wrong in clean_name:
                    clean_name = clean_name.replace(wrong, correct)
                    break
            
            # 숫자 제거 및 표준화
            clean_name = re.sub(r'\d+', '', clean_name)
            
            if not re.search(r'(정|캡슐|주사액|시럽|겔|크림|액|패치)$', clean_name):
                clean_name += '정'
            
            result.append(("UNKNOWN", clean_name))
        
        return list(set(result))
        
    except Exception as e:
        print(f"약품명 추출 중 오류 발생: {str(e)}")
        return []

def analyze_medical_record(text, medication_list=None):
    """진료기록 분석"""
    try:
        if not text or len(text.strip()) < 10:
            return "텍스트가 너무 짧거나 비어 있습니다."
        
        if client is None:
            return "OpenAI API 키가 설정되지 않았습니다."
        
        if not medication_list:
            meds = extract_medications(text)
            medication_list = [name for _, name in meds]
        
        # ChatGPT로 약품 정보 분석
        med_list_str = ", ".join(medication_list)
        
        prompt = f"""
        이것은 환자의 처방전입니다. 아래 내용을 이해하기 쉽게 설명해주세요.
        
        처방된 약품: {med_list_str}
        
        다음 세 개의 섹션으로 나누어 작성해주세요:
        
        [처방약 설명]
        각 약품별로:
        1. **약품명**
        • **효능은?** (효능을 간단히 설명)
        • **복용방법은?** (복용법을 간단히 설명)  
        • **주의사항은?** (주의사항을 간단히 설명)
        
        [생활 속 주의사항]
        • 식사: (내용)
        • 운동: (내용)
        • 수면: (내용)
        
        [약 복용 시 주의사항]
        • 복용 시간: (내용)
        • 복용 방법: (내용)
        • 보관법: (내용)
        • 부작용 관리: (내용)
        
        처방전 내용: {text}
        """
        
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "당신은 친절한 주치의입니다. 의학용어 대신 쉬운 말을 사용하고, 환자가 이해하기 쉽게 설명해주세요."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"AI 해석 오류: {str(e)}")
        return None

def get_drug_safety_info(drug_name):
    """의약품 안전정보 검색"""
    safety_results = {}
    
    # 약품명 전처리
    cleaned_name = re.sub(r'\([^)]*\)', '', drug_name).strip()
    cleaned_name = re.sub(r'^[^\w가-힣]+|[^\w가-힣]+$', '', cleaned_name)
    cleaned_name = re.sub(r'\s+', '', cleaned_name)
    search_name = re.sub(r'(정|캡슐|주사액|시럽|겔|크림|액|패치)$', '', cleaned_name)
    search_name = re.sub(r'\d+mg|\d+\.\d+mg', '', search_name)
    
    # 각 엔드포인트에 대해 검색 수행
    for endpoint_name, endpoint_path in DUR_ENDPOINTS.items():
        info_type = endpoint_name.replace("get", "").replace("03", "").replace("List", "")
        url = f"{API_KEYS['DUR_API_BASE_URL']}{endpoint_path}"
        
        params = {
            "serviceKey": API_KEYS["DUR_API_KEY"],
            "type": "json",
            "pageNo": "1",
            "numOfRows": "10",
            "itemName": search_name
        }
        
        try:
            session = requests.Session()
            response = session.get(url, params=params, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                header = data.get('header', {})
                body = data.get('body', {})
                
                result_code = header.get('resultCode', '알 수 없음')
                
                if result_code == '00':
                    total_count = body.get('totalCount', 0)
                    
                    if total_count > 0:
                        items = body.get('items', [])
                        if isinstance(items, dict):
                            items = items.get('item', [])
                            if not isinstance(items, list):
                                items = [items]
                        
                        safety_results[info_type] = items
                        
        except Exception:
            continue
    
    return safety_results

def text_to_speech(text, lang='ko'):
    """텍스트를 음성으로 변환"""
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filename = fp.name
            tts.save(temp_filename)
        
        with open(temp_filename, 'rb') as audio_file:
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
        
        os.unlink(temp_filename)
        return audio_base64
    except Exception as e:
        print(f"음성 변환 중 오류 발생: {str(e)}")
        return None 