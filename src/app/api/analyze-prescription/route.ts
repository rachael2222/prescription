import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    // 현재는 모의 응답을 반환
    // 실제 구현을 위해서는 Python 백엔드가 필요합니다
    
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json(
        { success: false, error: '파일이 없습니다.' },
        { status: 400 }
      )
    }

    // 모의 응답 (실제로는 Python 백엔드 호출 필요)
    const mockResponse = {
      success: true,
      data: {
        extracted_text: "처방전 텍스트 추출 결과입니다. 실제 OCR 기능을 위해서는 Python 백엔드가 필요합니다.",
        medications: ["타이레놀", "게보린", "소화제"],
        analysis: `분석 결과:

🔍 발견된 약품들:
- 타이레놀: 해열진통제
- 게보린: 두통 완화
- 소화제: 소화 개선

⚠️ 주의사항:
- 의사의 처방에 따라 복용하세요
- 부작용이 있을 시 즉시 병원에 문의하세요

💡 이것은 모의 응답입니다. 실제 AI 분석을 위해서는 OpenAI API와 Upstage OCR이 필요합니다.`
      }
    }

    return NextResponse.json(mockResponse)
    
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: '서버 오류가 발생했습니다. 실제 기능을 위해서는 Python 백엔드 배포가 필요합니다.' 
      },
      { status: 500 }
    )
  }
} 