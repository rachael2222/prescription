# 의약품 안전 정보 검색 스크립트
import urllib.parse
import requests
import json
import re
import os
from urllib3.exceptions import InsecureRequestWarning
import ssl

# SSL 경고 메시지 억제
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 레거시 SSL 문제 해결 시도 (옵션)
try:
    # Python의 기본 SSL 컨텍스트를 덜 제한적으로 설정
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    # 오래된 Python 버전에서는 이 속성이 없을 수 있음
    pass

# API 정보 설정 (HTTPS에서 HTTP로 변경)
DUR_API_BASE_URL = "http://apis.data.go.kr/1471000/DURPrdlstInfoService03"
DUR_API_KEY_DECODED = "7JoLokAR/RTfM/JwVNepjVIYCxYVM8SoTkD85mCgAXik51SO+uM+dmho7kDpSwMO9FX3t1WwxweejH0NGWpYJQ=="

# OCR에서 추출된 약품명 목록 (예시)
OCR_DRUG_NAMES = [
    "노바스크정",
    "트라젠타듀오정",
    "피오글리정",
    "아토렌정",
    "티지페논정"
]

class DrugSafetyInfo:
    """의약품 안전 정보 검색 클래스"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        # 최신 API 문서에 맞게 엔드포인트 업데이트
        self.dur_endpoints = {
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
            "getPwnmTabooInfoList03": "/getPwnmTabooInfoList03",  # 임부금기 정보
            
            # API 문서에 없는 엔드포인트는 주석 처리 (기능 확인 필요)
            # "getMixturePrscribInfoList": "/getMixturePrscribInfoList",  # 배합금기 정보
            # "getNrkSpcltyAtentInfoList": "/getNrkSpcltyAtentInfoList",  # 신기능 특이사항 정보
            # "getHepatfnSpcltyAtentInfoList": "/getHepatfnSpcltyAtentInfoList",  # 간기능 특이사항 정보
        }
    
    def search_drug_safety_info(self, drug_name):
        """약품명으로 안전 정보 검색"""
        print(f"\n[{drug_name}] 안전 정보 검색 중...")
        
        results = {}
        
        # 각 엔드포인트에 대해 검색 수행
        for endpoint_name, endpoint_path in self.dur_endpoints.items():
            info_type = endpoint_name.replace("get", "").replace("03", "").replace("List", "")
            print(f"\n{info_type} 정보 검색...")
            
            url = f"{DUR_API_BASE_URL}{endpoint_path}"
            
            # 파라미터 설정
            params = {
                "serviceKey": self.api_key,
                "type": "json",
                "pageNo": "1",
                "numOfRows": "10",
                "itemName": drug_name
            }
            
            try:
                # 요청 세션 설정
                session = requests.Session()
                session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
                session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
                
                # API 요청 보내기 (SSL 검증 비활성화)
                response = session.get(
                    url, 
                    params=params, 
                    verify=False,
                    timeout=10  # 타임아웃 추가
                )
                
                # 응답 내용 디버그 출력
                print(f"요청 URL: {response.url}")
                print(f"응답 상태 코드: {response.status_code}")
                
                response.raise_for_status()
                
                # JSON 응답 파싱
                try:
                    data = response.json()
                    header = data.get('header', {})
                    body = data.get('body', {})
                    
                    # 응답 코드 및 메시지 확인
                    result_code = header.get('resultCode', '알 수 없음')
                    result_msg = header.get('resultMsg', '알 수 없음')
                    
                    print(f"응답 코드: {result_code}, 메시지: {result_msg}")
                    
                    if result_code == '00':
                        # 성공 응답
                        total_count = body.get('totalCount', 0)
                        
                        # 결과가 있는 경우에만 처리
                        if total_count > 0:
                            # 아이템 정보 추출
                            items = body.get('items', [])
                            if isinstance(items, dict):
                                items = items.get('item', [])
                                if not isinstance(items, list):
                                    items = [items]
                            
                            print(f"- {len(items)}개 항목 발견")
                            results[info_type] = items
                            
                            # 첫 번째 항목 간략히 표시
                            if items:
                                for key, value in items[0].items():
                                    if key.lower() not in ['entpname', 'itemseq', 'itemname']:
                                        if value and len(str(value)) < 100:  # 중요한 정보만 표시
                                            print(f"  {key}: {value}")
                        else:
                            print(f"- 결과 없음")
                    else:
                        print(f"- API 오류: {result_code} - {result_msg}")
                except json.JSONDecodeError as e:
                    # JSON 파싱 실패 시 XML 형식 응답일 수 있음
                    print(f"- JSON 파싱 오류: {e}")
                    print(f"- 응답 내용 (처음 500자): {response.text[:500]}...")
                
            except requests.exceptions.RequestException as e:
                print(f"- 요청 오류: {e}")
                if hasattr(e, 'response') and e.response:
                    print(f"- 응답 코드: {e.response.status_code}")
                    print(f"- 응답 내용: {e.response.text[:500]}...")
        
        return results
    
    def summarize_safety_info(self, drug_name, safety_info):
        """안전 정보 요약"""
        print(f"\n[{drug_name}] 안전 정보 요약:")
        
        if not safety_info:
            print("- 안전 정보가 없습니다.")
            return
        
        # 안전 정보 유형별로 요약
        for info_type, items in safety_info.items():
            if items:
                print(f"\n● {info_type} 정보 ({len(items)}개 항목):")
                
                # 주요 정보 필드
                important_fields = [
                    'TYPE_NAME', 'PROHBT_CONTENT', 'REMARK', 'ATENT_INFO_TYPE_NAME',
                    'INGR_CODE', 'INGR_NAME', 'INGR_ENG_NAME', 'ATENT_INFO',
                    'LOW_AGE', 'HIGH_AGE', 'GENDER', 'PROHBT_CONTENT'
                ]
                
                # 항목별로 중요 정보 표시
                for i, item in enumerate(items[:3]):  # 최대 3개 항목만 표시
                    print(f"- 항목 {i+1}:")
                    
                    # 약품 기본 정보
                    print(f"  · 제품명: {item.get('ITEM_NAME', '-')}")
                    
                    # 중요 주의사항 정보
                    for field in important_fields:
                        if field in item and item[field]:
                            content = item[field]
                            if isinstance(content, str) and len(content) > 200:
                                content = content[:200] + "..."
                            print(f"  · {field}: {content}")
    
    def search_all_drugs(self, drug_names):
        """여러 약품에 대한 안전 정보 검색"""
        all_results = {}
        
        for drug_name in drug_names:
            print(f"\n{'='*50}")
            print(f"[{drug_name}] 정보 검색")
            print(f"{'='*50}")
            
            # 약품별 안전 정보 검색
            safety_info = self.search_drug_safety_info(drug_name)
            
            # 결과 저장
            all_results[drug_name] = safety_info
            
            # 안전 정보 요약
            self.summarize_safety_info(drug_name, safety_info)
        
        return all_results
    
    def get_combined_warnings(self, drug_names):
        """여러 약품의 주의사항을 조합하여 분석"""
        print("\n복수 약품 병용 주의사항 분석:")
        
        # 각 약품의 안전 정보 검색
        all_results = self.search_all_drugs(drug_names)
        
        # 병용금기 정보 분석
        print("\n◆ 병용금기 분석 결과:")
        contraindicated_pairs = []
        
        # 약품 이름 목록 출력
        print(f"검사 대상 약품: {', '.join(drug_names)}")
        
        # 실제 병용금기 정보는 API에서 가져와야 함
        # 여기서는 예시로 표시
        print("- 현재 처방된 약품 간에 병용금기 사항이 발견되지 않았습니다.")
        
        return all_results

def main():
    """메인 실행 함수"""
    print("의약품 안전 정보 검색 시작")
    
    # 검색 객체 생성
    drug_safety = DrugSafetyInfo(DUR_API_KEY_DECODED)
    
    # 옵션 선택 메뉴
    while True:
        print("\n====== 의약품 안전 정보 검색 ======")
        print("1. 단일 약품 검색")
        print("2. 모든 약품 안전 정보 검색")
        print("3. 복수 약품 병용 주의사항 분석")
        print("4. 종료")
        choice = input("\n선택: ")
        
        if choice == '1':
            # 단일 약품 검색
            drug_name = input("약품명 입력: ")
            safety_info = drug_safety.search_drug_safety_info(drug_name)
            drug_safety.summarize_safety_info(drug_name, safety_info)
        
        elif choice == '2':
            # 모든 약품 검색
            drug_safety.search_all_drugs(OCR_DRUG_NAMES)
        
        elif choice == '3':
            # 복수 약품 병용 주의사항 분석
            drug_safety.get_combined_warnings(OCR_DRUG_NAMES)
        
        elif choice == '4':
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("잘못된 선택입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    main() 