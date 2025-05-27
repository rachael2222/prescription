'use client'

import { useState } from 'react'
import { FileUpload } from '@/components/FileUpload'
import { AnalysisResult } from '@/components/AnalysisResult'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { analyzeImage, convertTextToSpeech } from '@/lib/api'

export interface AnalysisData {
  extracted_text: string
  medications: string[]
  analysis: string
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile)
    setResult(null)
    setError(null)
    setAudioUrl(null)
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError('파일을 선택해주세요.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const analysisResult = await analyzeImage(file)
      setResult(analysisResult)
    } catch (err: any) {
      setError(err.message || '분석 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handlePlayAudio = async () => {
    if (!result?.analysis) return

    try {
      const audioData = await convertTextToSpeech(result.analysis)
      const audioBlob = new Blob([Uint8Array.from(atob(audioData), c => c.charCodeAt(0))], {
        type: 'audio/mp3'
      })
      const url = URL.createObjectURL(audioBlob)
      setAudioUrl(url)

      const audio = new Audio(url)
      audio.play()
    } catch (err) {
      setError('음성 변환 중 오류가 발생했습니다.')
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-8">
          <FileUpload
            file={file}
            onFileSelect={handleFileSelect}
            onAnalyze={handleAnalyze}
            loading={loading}
          />

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700">❌ {error}</p>
            </div>
          )}

          {result && (
            <AnalysisResult
              result={result}
              onPlayAudio={handlePlayAudio}
              audioUrl={audioUrl}
            />
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
} 