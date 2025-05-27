import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    // 즉시 응답을 위한 최적화된 모의 API
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json(
        { success: false, error: '파일이 없습니다.' },
        { status: 400 }
      )
    }

    // 즉시 응답 - 상세한 모의 데이터 (원본 복구)
    const mockResponse = {
      success: true,
      data: {
        extracted_text: `○○병원 처방전
환자명: 홍길동
진료과: 내과
처방일: 2024-01-25

1. 타이레놀정 500mg - 1일 3회, 식후 30분
2. 게보린정 - 1일 2회, 아침/저녁 식후
3. 소화제 - 1일 3회, 식전 30분

※ 실제 OCR로 추출된 텍스트가 아닙니다.`,
        medications: ["타이레놀정 500mg", "게보린정", "소화제"],
        analysis: `🏥 처방전 분석 결과

📋 처방 정보:
• 환자: 홍길동
• 진료과: 내과  
• 처방일: 2024-01-25

💊 처방된 약물:
1. **타이레놀정 500mg** (아세트아미노펜)
   - 용법: 1일 3회, 식후 30분
   - 효능: 해열, 진통
   - 주의: 하루 최대 4000mg 초과 금지

2. **게보린정** (이부프로펜)
   - 용법: 1일 2회, 아침/저녁 식후
   - 효능: 소염, 진통, 해열
   - 주의: 위장장애 가능, 식후 복용 필수

3. **소화제**
   - 용법: 1일 3회, 식전 30분
   - 효능: 소화 촉진
   - 주의: 충분한 물과 함께 복용

⚠️ 복용 시 주의사항:
• 정해진 용법·용량을 준수하세요
• 알레르기 반응 시 즉시 복용 중단
• 다른 약물과의 상호작용 주의
• 증상 지속 시 재진료 받으세요

🔬 상호작용 검토:
• 타이레놀-게보린: 병용 가능 (간격 유지)
• 특별한 금기사항 없음

💡 이는 데모용 분석 결과입니다. 실제 의료진의 지시를 따르세요.`
      }
    }

    // 응답 반환

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