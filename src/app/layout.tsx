import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '처방전 분석기 - AI 기반 의료 정보 서비스',
  description: '처방전 사진을 업로드하면 AI가 약품 정보를 분석해드립니다.',
  keywords: '처방전, 의료, AI, 약품분석, 건강관리',
  authors: [{ name: 'Prescription Analyzer Team' }],
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
          {children}
        </div>
      </body>
    </html>
  )
} 