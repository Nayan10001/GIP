import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30 seconds timeout for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 503) {
      console.error('Service unavailable - check backend connection')
    } else if (error.response?.status >= 500) {
      console.error('Server error:', error.response.data)
    } else if (error.response?.status === 404) {
      console.error('Resource not found')
    }
    return Promise.reject(error)
  }
)

export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Get stats
  getStats: () => api.get('/stats'),

  // Extract from image
  extractFromImage: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post('/extract/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // Extract from text
  extractFromText: (text) => {
    return api.post('/extract/text', {
      invoice_text: text
    })
  },

  // Get extraction by ID
  getExtraction: (extractionId) => {
    return api.get(`/extraction/${extractionId}`)
  },

  // Get all extractions
  getExtractions: () => api.get('/extractions'),

  // Delete extraction
  deleteExtraction: (extractionId) => {
    return api.delete(`/extraction/${extractionId}`)
  },

  // Download extraction
  downloadExtraction: (extractionId) => {
    return api.get(`/extraction/${extractionId}/download`, {
      responseType: 'blob',
    }).then(response => {
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      // Try to get filename from response headers
      const contentDisposition = response.headers['content-disposition']
      let filename = `gst_invoice_${extractionId}.json`
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }
      
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    })
  },
}

export default apiService