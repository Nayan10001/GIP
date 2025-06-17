import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { apiService } from '../services/apiService'

const ResultsPage = () => {
  const { extractionId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchExtractionData()
  }, [extractionId])

  const fetchExtractionData = async () => {
    try {
      const response = await apiService.getExtraction(extractionId)
      setData(response.data)
    } catch (error) {
      console.error('Error fetching extraction data:', error)
      setError('Failed to load extraction data')
    } finally {
      setLoading(false)
    }
  }

  const downloadData = async () => {
    try {
      await apiService.downloadExtraction(extractionId)
    } catch (error) {
      console.error('Error downloading data:', error)
      alert('Failed to download data')
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Copied to clipboard!')
    }).catch(() => {
      alert('Failed to copy to clipboard')
    })
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount)
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
          <p className="text-gray-600">Loading extraction results...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <i className="fas fa-exclamation-triangle text-4xl text-red-500 mb-4"></i>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Data</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link to="/extract" className="btn-primary">
            Try Again
          </Link>
        </div>
      </div>
    )
  }

  const invoiceData = data.data

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Extraction Results
            </h1>
            <p className="text-gray-600">
              Extraction ID: <span className="font-mono text-sm">{extractionId}</span>
            </p>
            <p className="text-gray-600">
              Processed: {new Date(data.timestamp).toLocaleString()}
            </p>
          </div>
          <div className="flex space-x-4 mt-4 md:mt-0">
            <button
              onClick={downloadData}
              className="btn-secondary"
            >
              <i className="fas fa-download mr-2"></i>
              Download JSON
            </button>
            <Link to="/extract" className="btn-primary">
              <i className="fas fa-plus mr-2"></i>
              New Extraction
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Supplier Details */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <i className="fas fa-building text-primary-600 mr-2"></i>
              Supplier Details
            </h2>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Name</label>
                <div className="flex items-center justify-between">
                  <p className="text-gray-900">{invoiceData.supplier_details.name || 'N/A'}</p>
                  <button
                    onClick={() => copyToClipboard(invoiceData.supplier_details.name)}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    <i className="fas fa-copy"></i>
                  </button>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">GSTIN</label>
                <div className="flex items-center justify-between">
                  <p className="text-gray-900 font-mono">{invoiceData.supplier_details.gstin || 'N/A'}</p>
                  <button
                    onClick={() => copyToClipboard(invoiceData.supplier_details.gstin)}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    <i className="fas fa-copy"></i>
                  </button>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Address</label>
                <p className="text-gray-900 whitespace-pre-line">{invoiceData.supplier_details.address || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Recipient Details */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <i className="fas fa-user text-primary-600 mr-2"></i>
              Recipient Details
            </h2>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Name</label>
                <div className="flex items-center justify-between">
                  <p className="text-gray-900">{invoiceData.recipient_details.name || 'N/A'}</p>
                  <button
                    onClick={() => copyToClipboard(invoiceData.recipient_details.name)}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    <i className="fas fa-copy"></i>
                  </button>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">GSTIN</label>
                <div className="flex items-center justify-between">
                  <p className="text-gray-900 font-mono">{invoiceData.recipient_details.gstin || 'N/A'}</p>
                  <button
                    onClick={() => copyToClipboard(invoiceData.recipient_details.gstin)}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    <i className="fas fa-copy"></i>
                  </button>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Address</label>
                <p className="text-gray-900 whitespace-pre-line">{invoiceData.recipient_details.address || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Invoice Details */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <i className="fas fa-file-invoice text-primary-600 mr-2"></i>
              Invoice Details
            </h2>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Invoice Number</label>
                <div className="flex items-center justify-between">
                  <p className="text-gray-900 font-mono">{invoiceData.invoice_details.invoice_number || 'N/A'}</p>
                  <button
                    onClick={() => copyToClipboard(invoiceData.invoice_details.invoice_number)}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    <i className="fas fa-copy"></i>
                  </button>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Date</label>
                <p className="text-gray-900">{invoiceData.invoice_details.date || 'N/A'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Place of Supply</label>
                <p className="text-gray-900">{invoiceData.invoice_details.place_of_supply || 'N/A'}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Terms</label>
                <p className="text-gray-900">{invoiceData.invoice_details.terms || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Total Values */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <i className="fas fa-calculator text-primary-600 mr-2"></i>
              Total Values
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal:</span>
                <span className="font-semibold">{formatCurrency(invoiceData.total_values.subtotal)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">CGST Total:</span>
                <span className="font-semibold">{formatCurrency(invoiceData.total_values.cgst_total)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">SGST Total:</span>
                <span className="font-semibold">{formatCurrency(invoiceData.total_values.sgst_total)}</span>
              </div>
              {invoiceData.total_values.igst_total > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">IGST Total:</span>
                  <span className="font-semibold">{formatCurrency(invoiceData.total_values.igst_total)}</span>
                </div>
              )}
              <div className="border-t pt-3 flex justify-between">
                <span className="text-lg font-semibold text-gray-900">Total Amount:</span>
                <span className="text-lg font-bold text-primary-600">
                  {formatCurrency(invoiceData.total_values.total_invoice_value_numbers)}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                <strong>In Words:</strong> {invoiceData.total_values.total_invoice_value_words}
              </div>
            </div>
          </div>
        </div>

        {/* Items Table */}
        <div className="card p-6 mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <i className="fas fa-list text-primary-600 mr-2"></i>
            Items ({invoiceData.items.length})
          </h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    HSN/SAC
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Qty
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Taxable Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    CGST
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    SGST
                  </th>
                  {invoiceData.items.some(item => item.igst_rate > 0) && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      IGST
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {invoiceData.items.map((item, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                      {item.hsn_sac_code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(item.rate)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(item.taxable_value)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.cgst_rate}% ({formatCurrency(item.cgst_amount)})
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.sgst_rate}% ({formatCurrency(item.sgst_amount)})
                    </td>
                    {invoiceData.items.some(item => item.igst_rate > 0) && (
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.igst_rate > 0 ? `${item.igst_rate}% (${formatCurrency(item.igst_amount)})` : '-'}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Additional Notes */}
        {(invoiceData.additional_notes.signature || invoiceData.additional_notes.bank_details || invoiceData.additional_notes.other_notes) && (
          <div className="card p-6 mt-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <i className="fas fa-sticky-note text-primary-600 mr-2"></i>
              Additional Notes
            </h2>
            <div className="space-y-4">
              {invoiceData.additional_notes.signature && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Signature</label>
                  <p className="text-gray-900">{invoiceData.additional_notes.signature}</p>
                </div>
              )}
              {invoiceData.additional_notes.bank_details && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Bank Details</label>
                  <p className="text-gray-900 whitespace-pre-line">{invoiceData.additional_notes.bank_details}</p>
                </div>
              )}
              {invoiceData.additional_notes.other_notes && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Other Notes</label>
                  <p className="text-gray-900 whitespace-pre-line">{invoiceData.additional_notes.other_notes}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ResultsPage