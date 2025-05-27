'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface FileUploadProps {
  file: File | null
  onFileSelect: (file: File) => void
  onAnalyze: () => void
  loading: boolean
}

export function FileUpload({ file, onFileSelect, onAnalyze, loading }: FileUploadProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const uploadedFile = acceptedFiles[0]
    if (uploadedFile) {
      onFileSelect(uploadedFile)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    multiple: false
  })

  return (
    <div className="card">
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        {file ? (
          <div className="space-y-4">
            <img 
              src={URL.createObjectURL(file)} 
              alt="업로드된 처방전" 
              className="max-w-sm max-h-48 mx-auto rounded-lg shadow-md"
            />
            <p className="text-gray-700 font-medium">{file.name}</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-6xl">📄</div>
            <div>
              <p className="text-lg font-medium text-gray-700">
                {isDragActive
                  ? '파일을 여기에 놓으세요...'
                  : '처방전 이미지를 드래그하거나 클릭하여 업로드하세요'}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                JPG, PNG 파일만 지원됩니다
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 text-center">
        <button 
          onClick={onAnalyze} 
          disabled={!file || loading}
          className="btn-primary"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              분석 중...
            </span>
          ) : (
            '처방전 분석하기'
          )}
        </button>
      </div>
    </div>
  )
} 