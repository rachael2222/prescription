import streamlit as st
from PIL import Image
import requests
import tempfile
import os

# 페이지 설정
st.set_page_config(
    page_title="처방전 분석기 (Simple)",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def simple_ocr_placeholder(image):
    """OCR 기능 플레이스홀더"""
    return "처방전 텍스트 추출 기능은 API 키 설정 후 사용 가능합니다."

def main():
    st.title("🏥 처방전 분석기 (테스트 버전)")
    
    # 안내 메시지
    st.info("📋 이것은 배포 테스트를 위한 간단한 버전입니다. 실제 AI 분석 기능은 API 키 설정 후 사용할 수 있습니다.")
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "처방전 이미지를 업로드하세요",
        type=['png', 'jpg', 'jpeg'],
        help="PNG, JPG, JPEG 파일을 지원합니다."
    )
    
    if uploaded_file is not None:
        # 이미지 표시
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 처방전", use_column_width=True)
        
        # 분석 버튼
        if st.button("📝 처방전 분석하기", type="primary"):
            with st.spinner("이미지를 분석 중입니다..."):
                # 플레이스홀더 텍스트
                extracted_text = simple_ocr_placeholder(image)
                
                st.success("✅ 이미지 업로드 성공!")
                
                # 결과 표시
                st.subheader("📋 추출된 텍스트")
                st.text_area("OCR 결과", extracted_text, height=200)
                
                st.subheader("🎯 처방전 분석 결과")
                st.markdown("""
                ### 📊 테스트 분석 결과
                
                **🔧 현재 상태:** 배포 테스트 모드
                
                **📋 필요한 설정:**
                - OpenAI API 키
                - Upstage OCR API 키  
                - DUR API 키
                
                **✅ 앱 배포:** 성공!
                **🚀 다음 단계:** API 키 설정 후 전체 기능 활성화
                """)
    
    # 사이드바 정보
    with st.sidebar:
        st.header("📖 사용 방법")
        st.markdown("""
        1. **이미지 업로드**: 처방전 사진 선택
        2. **분석 시작**: '처방전 분석하기' 버튼 클릭  
        3. **결과 확인**: 추출된 정보 검토
        """)
        
        st.header("⚙️ 시스템 정보")
        st.markdown(f"""
        - **Streamlit 버전**: {st.__version__}
        - **Python 환경**: 정상 작동
        - **이미지 처리**: Pillow 사용 가능
        - **네트워크**: requests 사용 가능
        """)

if __name__ == "__main__":
    main() 