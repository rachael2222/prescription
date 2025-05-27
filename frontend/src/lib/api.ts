import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

export interface AnalysisResponse {
  success: boolean
  data: {
    extracted_text: string
    medications: string[]
    analysis: string
  }
}

export interface TextToSpeechResponse {
  success: boolean
  audio_data: string
}

export const analyzeImage = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<AnalysisResponse>('/api/analyze-prescription', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  if (!response.data.success) {
    throw new Error('분석에 실패했습니다.')
  }

  return response.data.data
}

export const convertTextToSpeech = async (text: string): Promise<string> => {
  const response = await api.post<TextToSpeechResponse>('/api/text-to-speech', null, {
    params: { text }
  })

  if (!response.data.success) {
    throw new Error('음성 변환에 실패했습니다.')
  }

  return response.data.audio_data
}

export const getDrugInfo = async (drugName: string) => {
  const response = await api.get(`/api/drug-info/${drugName}`)
  return response.data
} 