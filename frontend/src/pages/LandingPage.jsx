import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiService } from '../services/apiService'

const LandingPage = () => {
  const [stats, setStats] = useState({
    total_extractions: 0,
    total_invoice_amount: 0,
    unique_suppliers: 0,
    api_status: 'loading'
  })

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await apiService.getStats()
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
      setStats(prev => ({ ...prev, api_status: 'error' }))
    }
  }

  const features = [
    {
      icon: 'fas fa-robot',
      title: 'AI-Powered Extraction',
      description: 'Advanced Gemini AI technology extracts data from GST invoices with high accuracy and speed.'
    },
    {
      icon: 'fas fa-file-upload',
      title: 'Multiple Input Methods',
      description: 'Upload invoice images or paste text directly. Supports JPG, PNG, PDF and more formats.'
    },
    {
      icon: 'fas fa-shield-alt',
      title: 'Secure & Compliant',
      description: 'Your invoice data is processed securely with enterprise-grade security measures.'
    },
    {
      icon: 'fas fa-download',
      title: 'Export Ready Data',
      description: 'Download extracted data in JSON format, ready for integration with your systems.'
    },
    {
      icon: 'fas fa-clock',
      title: 'Real-time Processing',
      description: 'Get instant results with our fast processing engine. No waiting, no delays.'
    },
    {
      icon: 'fas fa-chart-line',
      title: 'Analytics Dashboard',
      description: 'Track your extraction history and get insights into your invoice processing.'
    }
  ]

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount)
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <div className="animate-fade-in">
              <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
                Extract GST Invoice Data
                <span className="block text-primary-600">with AI Precision</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
                Transform your invoice processing workflow with our AI-powered GST invoice data extraction tool. 
                Get structured data from invoices in seconds, not hours.
              </p>
            </div>
            
            <div className="animate-slide-up flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Link to="/extract" className="btn-primary text-lg px-8 py-4">
                <i className="fas fa-rocket mr-2"></i>
                Start Extracting Now
              </Link>
              <a href="#features" className="btn-secondary text-lg px-8 py-4">
                <i className="fas fa-info-circle mr-2"></i>
                Learn More
              </a>
            </div>

            {/* Stats Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="card p-6 text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {stats.total_extractions.toLocaleString()}
                </div>
                <div className="text-gray-600">Invoices Processed</div>
              </div>
              <div className="card p-6 text-center">
                <div className="text-3xl font-bold text-success-600 mb-2">
                  {formatCurrency(stats.total_invoice_amount)}
                </div>
                <div className="text-gray-600">Total Value Processed</div>
              </div>
              <div className="card p-6 text-center">
                <div className="text-3xl font-bold text-warning-600 mb-2">
                  {stats.unique_suppliers}
                </div>
                <div className="text-gray-600">Unique Suppliers</div>
              </div>
            </div>
          </div>
        </div>

        {/* Background decoration */}
        <div className="absolute top-0 right-0 -mt-20 -mr-20 w-80 h-80 bg-primary-100 rounded-full opacity-20 animate-pulse-slow"></div>
        <div className="absolute bottom-0 left-0 -mb-20 -ml-20 w-60 h-60 bg-blue-100 rounded-full opacity-20 animate-bounce-slow"></div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Businesses
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our GST invoice parser is designed to handle the complexities of Indian taxation 
              and invoice formats with precision and reliability.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="card p-8 text-center group">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 text-primary-600 rounded-full mb-6 group-hover:bg-primary-600 group-hover:text-white transition-all duration-300">
                  <i className={`${feature.icon} text-2xl`}></i>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Extract GST invoice data in three simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-600 text-white rounded-full text-2xl font-bold mb-6">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Upload Invoice
              </h3>
              <p className="text-gray-600">
                Upload your GST invoice image or paste the invoice text directly into our system.
              </p>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-600 text-white rounded-full text-2xl font-bold mb-6">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                AI Processing
              </h3>
              <p className="text-gray-600">
                Our advanced AI analyzes the invoice and extracts all relevant GST data fields automatically.
              </p>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-600 text-white rounded-full text-2xl font-bold mb-6">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Get Results
              </h3>
              <p className="text-gray-600">
                Receive structured data in JSON format, ready for integration with your accounting systems.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Automate Your Invoice Processing?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-3xl mx-auto">
            Join thousands of businesses who trust our AI-powered GST invoice parser 
            to streamline their accounting workflows.
          </p>
          <Link to="/extract" className="inline-flex items-center bg-white text-primary-600 font-semibold py-4 px-8 rounded-lg hover:bg-gray-50 transition-all duration-200 transform hover:scale-105">
            <i className="fas fa-play mr-2"></i>
            Start Free Trial
          </Link>
        </div>
      </section>
    </div>
  )
}

export default LandingPage