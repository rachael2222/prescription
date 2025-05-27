export function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            🏥 처방전 분석기
          </h1>
          <p className="text-xl md:text-2xl opacity-90">
            처방전 사진을 업로드하면 AI가 약품 정보를 분석해드립니다.
          </p>
        </div>
      </div>
    </header>
  )
} 