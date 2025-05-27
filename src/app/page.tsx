export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🏥 처방전 분석기
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            AI 기반 의료 정보 서비스
          </p>
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
            <h2 className="text-2xl font-semibold mb-4">서비스 준비 중</h2>
            <p className="text-gray-600">
              처방전 사진을 업로드하면 AI가 약품 정보를 분석해드립니다.
            </p>
            <div className="mt-6">
              <button className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                곧 서비스 예정
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 