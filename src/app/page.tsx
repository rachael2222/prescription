'use client'

import { useState } from 'react'
import { analyzeImage } from '@/lib/api'

interface AnalysisResult {
  extracted_text: string
  medications: string[]
  analysis: string
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
      setResult(null)
    }
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
    } catch (err) {
      setError('분석 중 오류가 발생했습니다. 백엔드 서버가 실행 중인지 확인해주세요.')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🏥 처방전 분석기
          </h1>
          <p className="text-xl text-gray-600">
            AI 기반 의료 정보 서비스
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* 파일 업로드 섹션 */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-4">처방전 업로드</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <div className="text-4xl mb-2">📄</div>
                <p className="text-gray-600 mb-2">
                  {file ? file.name : '처방전 이미지를 선택하세요'}
                </p>
                <p className="text-sm text-gray-500">
                  JPG, PNG, GIF 파일 지원
                </p>
              </label>
            </div>
            
            {file && (
              <div className="mt-4 text-center">
                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  {loading ? '분석 중...' : '분석 시작'}
                </button>
              </div>
            )}
          </div>

          {/* 오류 메시지 */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <div className="text-red-500 mr-2">⚠️</div>
                <p className="text-red-700">{error}</p>
              </div>
              <div className="mt-2 text-sm text-red-600">
                <p>💡 해결 방법:</p>
                <ul className="list-disc list-inside ml-4">
                  <li>백엔드 서버가 실행 중인지 확인하세요</li>
                  <li>API 키가 올바르게 설정되었는지 확인하세요</li>
                  <li>네트워크 연결을 확인하세요</li>
                </ul>
              </div>
            </div>
          )}

          {/* 분석 결과 */}
          {result && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">분석 결과</h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-2">추출된 텍스트</h3>
                  <div className="bg-gray-50 rounded p-3 text-sm">
                    {result.extracted_text}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-2">발견된 약품</h3>
                  <div className="flex flex-wrap gap-2">
                    {result.medications.map((med, index) => (
                      <span
                        key={index}
                        className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                      >
                        {med}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-2">AI 분석</h3>
                  <div className="bg-green-50 rounded p-4 text-sm whitespace-pre-wrap">
                    {result.analysis}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 서비스 안내 */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
            <div className="flex items-center">
              <div className="text-blue-600 mr-2">🚀</div>
              <div>
                <p className="text-blue-800 font-medium">데모 버전</p>
                <p className="text-blue-700 text-sm">
                  현재 모의 데이터로 작동합니다. 실제 AI 분석을 위해서는 Railway에 백엔드를 배포해야 합니다.
                  <br />
                  <strong>테스트:</strong> 파일명에 "prescription" 또는 "처방전"을 포함하여 업로드해보세요!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 