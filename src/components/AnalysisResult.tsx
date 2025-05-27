'use client'

import ReactMarkdown from 'react-markdown'
import { AnalysisData } from '@/types'

interface AnalysisResultProps {
  result: AnalysisData
  onPlayAudio: () => void
  audioUrl: string | null
}

export function AnalysisResult({ result, onPlayAudio, audioUrl }: AnalysisResultProps) {
  const formatAnalysis = (analysis: string) => {
    if (!analysis) return ''
    
    // 섹션별로 나누어 표시
    const sections = analysis.split(/\[([^\]]+)\]/)
    let formattedText = ''
    
    for (let i = 1; i < sections.length; i += 2) {
      const title = sections[i]
      const content = sections[i + 1] || ''
      
      formattedText += `## ${title}\n\n${content.trim()}\n\n`
    }
    
    return formattedText || analysis
  }

  return (
    <div className="card">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800">📋 분석 결과</h2>
        <button 
          onClick={onPlayAudio} 
          className="btn-secondary flex items-center gap-2"
        >
          🔊 음성으로 듣기
        </button>
      </div>

      {result.medications && result.medications.length > 0 && (
        <div className="bg-blue-50 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-blue-700 mb-4">💊 처방된 약품</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {result.medications.map((med, index) => (
              <div 
                key={index}
                className="bg-white px-4 py-2 rounded-md border-l-4 border-blue-500 shadow-sm"
              >
                {med}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="prose prose-lg max-w-none">
        <div className="text-gray-700 leading-relaxed">
          <ReactMarkdown
            components={{
              h2: ({ children }) => (
                <h2 className="text-xl font-bold text-blue-600 border-b-2 border-blue-200 pb-2 mb-4 mt-6">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-lg font-semibold text-purple-600 mb-3 mt-4">
                  {children}
                </h3>
              ),
              ul: ({ children }) => (
                <ul className="space-y-2 ml-4">
                  {children}
                </ul>
              ),
              li: ({ children }) => (
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span>{children}</span>
                </li>
              ),
              strong: ({ children }) => (
                <strong className="text-blue-600 font-semibold">
                  {children}
                </strong>
              ),
            }}
          >
            {formatAnalysis(result.analysis)}
          </ReactMarkdown>
        </div>
      </div>

      {audioUrl && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <audio 
            controls 
            src={audioUrl} 
            className="w-full"
          >
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  )
} 