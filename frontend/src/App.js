import React, { useState } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);

  const onDrop = (acceptedFiles) => {
    const uploadedFile = acceptedFiles[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      setResult(null);
      setError(null);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    multiple: false
  });

  const analyzeImage = async () => {
    if (!file) {
      setError('파일을 선택해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/analyze-prescription`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data.data);
    } catch (err) {
      setError(err.response?.data?.detail || '분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const playAudio = async () => {
    if (!result?.analysis) return;

    try {
      const response = await axios.post(`${API_BASE_URL}/api/text-to-speech`, null, {
        params: { text: result.analysis }
      });

      const audioData = response.data.audio_data;
      const audioBlob = new Blob([Uint8Array.from(atob(audioData), c => c.charCodeAt(0))], {
        type: 'audio/mp3'
      });
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      const audio = new Audio(url);
      audio.play();
    } catch (err) {
      setError('음성 변환 중 오류가 발생했습니다.');
    }
  };

  const formatAnalysis = (analysis) => {
    if (!analysis) return '';
    
    // 섹션별로 나누어 표시
    const sections = analysis.split(/\[([^\]]+)\]/);
    let formattedText = '';
    
    for (let i = 1; i < sections.length; i += 2) {
      const title = sections[i];
      const content = sections[i + 1] || '';
      
      formattedText += `## ${title}\n\n${content.trim()}\n\n`;
    }
    
    return formattedText || analysis;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏥 처방전 분석기</h1>
        <p>처방전 사진을 업로드하면 AI가 약품 정보를 분석해드립니다.</p>
      </header>

      <main className="App-main">
        <div className="upload-section">
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            {file ? (
              <div className="file-preview">
                <img 
                  src={URL.createObjectURL(file)} 
                  alt="업로드된 처방전" 
                  style={{ maxWidth: '300px', maxHeight: '200px' }}
                />
                <p>{file.name}</p>
              </div>
            ) : (
              <div className="upload-placeholder">
                <p>
                  {isDragActive
                    ? '파일을 여기에 놓으세요...'
                    : '처방전 이미지를 드래그하거나 클릭하여 업로드하세요'}
                </p>
                <p className="upload-hint">JPG, PNG 파일만 지원됩니다</p>
              </div>
            )}
          </div>

          <button 
            onClick={analyzeImage} 
            disabled={!file || loading}
            className="analyze-button"
          >
            {loading ? '분석 중...' : '처방전 분석하기'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <p>❌ {error}</p>
          </div>
        )}

        {result && (
          <div className="result-section">
            <div className="result-header">
              <h2>📋 분석 결과</h2>
              <button onClick={playAudio} className="audio-button">
                🔊 음성으로 듣기
              </button>
            </div>

            {result.medications && result.medications.length > 0 && (
              <div className="medications-list">
                <h3>💊 처방된 약품</h3>
                <ul>
                  {result.medications.map((med, index) => (
                    <li key={index}>{med}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="analysis-content">
              <ReactMarkdown>{formatAnalysis(result.analysis)}</ReactMarkdown>
            </div>

            {audioUrl && (
              <audio controls src={audioUrl} style={{ marginTop: '20px', width: '100%' }}>
                Your browser does not support the audio element.
              </audio>
            )}
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>© 2024 처방전 분석기 - AI 기반 의료 정보 서비스</p>
      </footer>
    </div>
  );
}

export default App; 