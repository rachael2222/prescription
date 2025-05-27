export interface AnalysisData {
  extracted_text: string
  medications: string[]
  analysis: string
}

export interface AnalysisResponse {
  success: boolean
  data: AnalysisData
}

export interface TextToSpeechResponse {
  success: boolean
  audio_data: string
} 