import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiService } from '../services/apiService'

const ExtractorPage = () => {
  const [activeTab, setActiveTab] = useState('image')
  const [file, setFile] = useState(null)
  const [textInput, setTextInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const navigate = useNavigate()

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (validateFile(droppedFile)) {
        setFile(droppedFile)
      }
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (validateFile(selectedFile)) {
        setFile(selectedFile)
      }
    }
  }

  const validateFile = (file) => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp']
    const maxSize = 10 * 1024 * 1024 // 10MB

    if (!allowedTypes.includes(file.type)) {
      alert('Please select a valid image file (JPG, PNG, BMP, TIFF, WEBP)')
      return false
    }

    if (file.size > maxSize) {
      alert('File size must be less than 10MB')
      return false
    }

    return true
  }

  const handleImageExtraction = async () => {
    if (!file) {
      alert('Please select a file first')
      return
    }

    setIsLoading(true)
    try {
      const response = await apiService.extractFromImage(file)
      if (response.data.success) {
        navigate(`/results/${response.data.extraction_id}`)
      } else {
        alert(response.data.message || 'Failed to extract data from image')
      }
    } catch (error) {
      console.error('Error extracting from image:', error)
      alert('Error processing image. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTextExtraction = async () => {
    if (!textInput.trim()) {
      alert('Please enter invoice text')
      return
    }

    setIsLoading(true)
    try {
      const response = await apiService.extractFromText(textInput)
      if (response.data.success) {
        navigate(`/results/${response.data.extraction_id}`)
      } else {
        alert(response.data.message || 'Failed to extract data from text')
      }
    } catch (error) {
      console.error('Error extracting from text:', error)
      alert('Error processing text. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Extract GST Invoice Data
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Upload an invoice image or paste invoice text to extract structured GST data using AI
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('image')}
              className={`px-6 py-3 rounded-md font-medium transition-all duration-200 ${
                activeTab === 'image'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <i className="fas fa-image mr-2"></i>
              Upload Image
            </button>
            <button
              onClick={() => setActiveTab('text')}
              className={`px-6 py-3 rounded-md font-medium transition-all duration-200 ${
                activeTab === 'text'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <i className="fas fa-keyboard mr-2"></i>
              Paste Text
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="card p-8">
          {activeTab === 'image' ? (
            <div>
              {/* File Upload Area */}
              <div
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-all duration-200 ${
                  dragActive
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <div className="mb-4">
                  <i className="fas fa-cloud-upload-alt text-4xl text-gray-400"></i>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Drop your invoice image here
                </h3>
                <p className="text-gray-600 mb-4">
                  or click to browse files
                </p>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="btn-secondary cursor-pointer inline-block"
                >
                  <i className="fas fa-folder-open mr-2"></i>
                  Choose File
                </label>
                <p className="text-sm text-gray-500 mt-4">
                  Supported formats: JPG, PNG, BMP, TIFF, WEBP (Max 10MB)
                </p>
              </div>

              {/* Selected File Info */}
              {file && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <i className="fas fa-file-image text-primary-600 text-xl"></i>
                      <div>
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-600">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setFile(null)}
                      className="text-red-500 hover:text-red-700 transition-colors duration-200"
                    >
                      <i className="fas fa-times text-xl"></i>
                    </button>
                  </div>
                </div>
              )}

              {/* Extract Button */}
              <div className="mt-8 text-center">
                <button
                  onClick={handleImageExtraction}
                  disabled={!file || isLoading}
                  className={`btn-primary text-lg px-8 py-4 ${
                    (!file || isLoading) ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {isLoading ? (
                    <>
                      <div className="loading-dots mr-2">
                        <div></div>
                        <div></div>
                        <div></div>
                        <div></div>
                      </div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-magic mr-2"></i>
                      Extract Data
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            <div>
              {/* Text Input Area */}
              <div className="mb-6">
                <label htmlFor="invoice-text" className="block text-lg font-semibold text-gray-900 mb-3">
                  Paste Invoice Text
                </label>
                <textarea
                  id="invoice-text"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Paste your GST invoice text here..."
                  className="input-field h-64 resize-none"
                  disabled={isLoading}
                />
                <p className="text-sm text-gray-500 mt-2">
                  Copy and paste the complete invoice text including all details like supplier info, items, taxes, etc.
                </p>
              </div>

              {/* Extract Button */}
              <div className="text-center">
                <button
                  onClick={handleTextExtraction}
                  disabled={!textInput.trim() || isLoading}
                  className={`btn-primary text-lg px-8 py-4 ${
                    (!textInput.trim() || isLoading) ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {isLoading ? (
                    <>
                      <div className="loading-dots mr-2">
                        <div></div>
                        <div></div>
                        <div></div>
                        <div></div>
                      </div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-magic mr-2"></i>
                      Extract Data
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Tips Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 text-primary-600 rounded-full mb-4">
              <i className="fas fa-lightbulb"></i>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">High Quality Images</h3>
            <p className="text-sm text-gray-600">
              Use clear, high-resolution images for better extraction accuracy
            </p>
          </div>
          <div className="text-center p-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-success-100 text-success-600 rounded-full mb-4">
              <i className="fas fa-check-circle"></i>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Complete Information</h3>
            <p className="text-sm text-gray-600">
              Ensure all invoice sections are visible and readable
            </p>
          </div>
          <div className="text-center p-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-warning-100 text-warning-600 rounded-full mb-4">
              <i className="fas fa-shield-alt"></i>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Secure Processing</h3>
            <p className="text-sm text-gray-600">
              Your data is processed securely and not stored permanently
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExtractorPage