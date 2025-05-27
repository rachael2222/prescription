from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import io
import base64
from typing import List, Dict, Any
import tempfile
import os

# 기존 함수들 import
from config import get_api_keys
from medical_functions import (
    upstage_ocr, 
    extract_medications, 
    analyze_medical_record,
    get_drug_safety_info,
    text_to_speech
)

app = FastAPI(title="Medical Prescription API", version="1.0.0")

# CORS 설정 (React 앱에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Medical Prescription Analysis API"}

@app.post("/api/analyze-prescription")
async def analyze_prescription(file: UploadFile = File(...)):
    """처방전 이미지를 분석하여 약품 정보와 설명을 반환"""
    try:
        # 파일 검증
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
        
        # 이미지 읽기
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # OCR로 텍스트 추출
        extracted_text = upstage_ocr(image)
        if not extracted_text:
            raise HTTPException(status_code=400, detail="텍스트 추출에 실패했습니다.")
        
        # 약품명 추출
        medications = extract_medications(extracted_text)
        medication_list = [name for _, name in medications]
        
        # AI 분석
        analysis = analyze_medical_record(extracted_text, medication_list)
        if not analysis:
            raise HTTPException(status_code=500, detail="분석에 실패했습니다.")
        
        return {
            "success": True,
            "data": {
                "extracted_text": extracted_text,
                "medications": medication_list,
                "analysis": analysis
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/text-to-speech")
async def convert_text_to_speech(text: str):
    """텍스트를 음성으로 변환"""
    try:
        audio_base64 = text_to_speech(text)
        if not audio_base64:
            raise HTTPException(status_code=500, detail="음성 변환에 실패했습니다.")
        
        return {
            "success": True,
            "audio_data": audio_base64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"음성 변환 중 오류: {str(e)}")

@app.get("/api/drug-info/{drug_name}")
async def get_drug_info(drug_name: str):
    """특정 약품의 안전 정보 조회"""
    try:
        safety_info = get_drug_safety_info(drug_name)
        return {
            "success": True,
            "drug_name": drug_name,
            "safety_info": safety_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"약품 정보 조회 중 오류: {str(e)}")

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "message": "API server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 