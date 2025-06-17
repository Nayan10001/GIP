import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiService } from '../services/apiService'

const HistoryPage = () => {
  const [extractions, setExtractions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchExtractions()
  }, [])

  const fetchExtractions = async () => {
    try {
      const response = await apiService.getExtractions()
      setExtractions(response.data.extractions)
    } catch (error) {
      console.error('Error fetching extractions:', error)
      setError('Failed to load extraction history')
    } finally {
      setLoading(false)
    }
  }

  const deleteExtraction = async (extractionId) => {
    if (!confirm('Are you sure you want to delete this extraction?')) {
      return
    }

    try {
      await apiService.deleteExtraction(extractionId)
      setExtractions(extractions.filter(ext => ext.extraction_id !== extractionId))
    } catch (error) {
      console.error('Error deleting extraction:', error)
      alert('Failed to delete extraction')
    }
  }

  const downloadExtraction = async (extractionId) => {
    try {
      await apiService.downloadExtraction(extractionId)
    } catch (error) {
      console.error('Error downloading extraction:', error)
      alert('Failed to download extraction')
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-dots mb-4">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
          <p className="text-gray-600">Loading extraction history...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <i className="fas fa-exclamation-triangle text-4xl text-red-500 mb-4"></i>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading History</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={fetchExtractions}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Extraction History
            </h1>
            <p className="text-gray-600">
              View and manage your previous GST invoice extractions
            </p>
          </div>
          <Link to="/extract" className="btn-primary mt-4 md:mt-0">
            <i className="fas fa-plus mr-2"></i>
            New Extraction
          </Link>
        </div>

        {extractions.length === 0 ? (
          <div className="text-center py-12">
            <i className="fas fa-history text-4xl text-gray-400 mb-4"></i>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No Extractions Yet</h2>
            <p className="text-gray-600 mb-6">
              You haven't processed any invoices yet. Start by uploading your first invoice.
            </p>
            <Link to="/extract" className="btn-primary">
              <i className="fas fa-upload mr-2"></i>
              Upload Invoice
            </Link>
          </div>
        ) : (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="card p-6 text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {extractions.length}
                </div>
                <div className="text-gray-600">Total Extractions</div>
              </div>
              <div className="card p-6 text-center">
                <div className="text-3xl font-bold text-success-600 mb-2">
                  {formatCurrency(extractions.reduce((sum, ext) => sum + ext.total_amount, 0))}
                </div>
                <div className="text-gray-600">Total Value Processed</div>
              </div>
              <div className="card p-6 text-center">
                <div className="text-3xl font-bold text-warning-600 mb-2">
                  {new Set(extractions.map(ext => ext.supplier_name)).size}
                </div>
                <div className="text-gray-600">Unique Suppliers</div>
              </div>
            </div>

            {/* Extractions Table */}
            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Invoice Details
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Supplier
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Processed
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {extractions.map((extraction) => (
                      <tr key={extraction.extraction_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {extraction.invoice_number}
                            </div>
                            <div className="text-sm text-gray-500 font-mono">
                              ID: {extraction.extraction_id.substring(0, 16)}...
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {extraction.supplier_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-semibold text-gray-900">
                            {formatCurrency(extraction.total_amount)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {formatDate(extraction.timestamp)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <Link
                              to={`/results/${extraction.extraction_id}`}
                              className="text-primary-600 hover:text-primary-900 transition-colors duration-200"
                              title="View Details"
                            >
                              <i className="fas fa-eye"></i>
                            </Link>
                            <button
                              onClick={() => downloadExtraction(extraction.extraction_id)}
                              className="text-success-600 hover:text-success-900 transition-colors duration-200"
                              title="Download JSON"
                            >
                              <i className="fas fa-download"></i>
                            </button>
                            <button
                              onClick={() => deleteExtraction(extraction.extraction_id)}
                              className="text-red-600 hover:text-red-900 transition-colors duration-200"
                              title="Delete"
                            >
                              <i className="fas fa-trash"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default HistoryPage