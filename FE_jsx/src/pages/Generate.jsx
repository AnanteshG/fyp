import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { generatePPT, uploadSource, checkMultipleUrls } from '../api'

export default function Generate() {
  const navigate = useNavigate()
  
  const [formData, setFormData] = useState({
    topic: '',
    urls: [],
    num_slides: 7,
    theme: 'modern',
    brand_colors: [],
    source_text: '',
    ai_provider: 'groq'
  })
  
  const [urlInput, setUrlInput] = useState('')
  const [urlCheckResults, setUrlCheckResults] = useState([])
  const [checkingUrls, setCheckingUrls] = useState(false)
  const [colorInput, setColorInput] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [uploadedText, setUploadedText] = useState('')

  const themes = [
    { value: 'modern', label: 'Modern', description: 'Clean, professional blue' },
    { value: 'dark', label: 'Dark', description: 'Dark background, light text' },
    { value: 'professional', label: 'Professional', description: 'Corporate gray tones' },
    { value: 'business', label: 'Business', description: 'Business-friendly styling' },
    { value: 'academic', label: 'Academic', description: 'Academic presentation style' },
    { value: 'minimal', label: 'Minimal', description: 'Minimalist black & white' },
    { value: 'creative', label: 'Creative', description: 'Warm, creative colors' }
  ]

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'num_slides' ? parseInt(value) : value
    }))
  }

  const handleAddUrl = async () => {
    if (urlInput.trim()) {
      const newUrls = [...formData.urls, urlInput.trim()]
      setFormData(prev => ({
        ...prev,
        urls: newUrls
      }))
      setUrlInput('')
      
      // Check the newly added URL
      setCheckingUrls(true)
      try {
        const results = await checkMultipleUrls([urlInput.trim()])
        setUrlCheckResults(prev => [...prev, ...results])
      } catch (err) {
        console.error('Failed to check URL:', err)
      } finally {
        setCheckingUrls(false)
      }
    }
  }

  const handleRemoveUrl = (index) => {
    setFormData(prev => ({
      ...prev,
      urls: prev.urls.filter((_, i) => i !== index)
    }))
    setUrlCheckResults(prev => prev.filter((_, i) => i !== index))
  }

  const handleCheckAllUrls = async () => {
    if (formData.urls.length === 0) return
    
    setCheckingUrls(true)
    try {
      const results = await checkMultipleUrls(formData.urls)
      setUrlCheckResults(results)
    } catch (err) {
      setError('Failed to check URLs for robots.txt compliance')
    } finally {
      setCheckingUrls(false)
    }
  }

  const handleAddColor = () => {
    if (colorInput.trim()) {
      setFormData(prev => ({
        ...prev,
        brand_colors: [...prev.brand_colors, colorInput.trim()]
      }))
      setColorInput('')
    }
  }

  const handleRemoveColor = (index) => {
    setFormData(prev => ({
      ...prev,
      brand_colors: prev.brand_colors.filter((_, i) => i !== index)
    }))
  }

  const handleFileUpload = async (e) => {
    const selectedFile = e.target.files[0]
    if (!selectedFile) return

    setFile(selectedFile)
    setLoading(true)
    setError('')

    try {
      const result = await uploadSource(selectedFile)
      setUploadedText(result.text)
      setFormData(prev => ({
        ...prev,
        source_text: result.text
      }))
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload file')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const result = await generatePPT(formData)
      navigate(`/editor/${result.ppt_id}`)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate presentation')
      setLoading(false)
    }
  }

  return (
    <div className="px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Generate Presentation</h1>
        <p className="text-gray-600 mb-8">
          Fill in the details below to create your AI-powered presentation
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
          {/* Topic */}
          <div>
            <label htmlFor="topic" className="block text-sm font-semibold text-gray-700 mb-2">
              Presentation Topic *
            </label>
            <input
              type="text"
              id="topic"
              name="topic"
              value={formData.topic}
              onChange={handleInputChange}
              required
              placeholder="e.g., Artificial Intelligence in Healthcare"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              If no URLs provided, we'll use Wikipedia to gather content
            </p>
          </div>

          {/* URLs to Scrape */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Websites to Scrape (Optional)
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddUrl())}
                placeholder="https://example.com/article"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={handleAddUrl}
                disabled={checkingUrls}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400"
              >
                {checkingUrls ? 'Checking...' : 'Add URL'}
              </button>
            </div>
            
            {formData.urls.length > 0 && (
              <div className="space-y-2 mb-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-600">
                    {formData.urls.length} URL(s) added
                  </span>
                  <button
                    type="button"
                    onClick={handleCheckAllUrls}
                    disabled={checkingUrls}
                    className="text-xs text-blue-600 hover:text-blue-700"
                  >
                    {checkingUrls ? 'Checking...' : 'Recheck All'}
                  </button>
                </div>
                
                {formData.urls.map((url, index) => {
                  const checkResult = urlCheckResults.find(r => r.url === url)
                  return (
                    <div
                      key={index}
                      className={`flex items-center justify-between p-3 rounded-md border ${
                        checkResult?.allowed 
                          ? 'bg-green-50 border-green-200' 
                          : checkResult 
                          ? 'bg-red-50 border-red-200'
                          : 'bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm truncate">{url}</p>
                        {checkResult && (
                          <p className={`text-xs mt-1 ${
                            checkResult.allowed ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {checkResult.allowed 
                              ? '✓ Scraping allowed' 
                              : `✗ ${checkResult.message || 'Scraping not allowed'}`
                            }
                          </p>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveUrl(index)}
                        className="ml-2 text-red-500 hover:text-red-700"
                      >
                        ×
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
            
            <p className="text-xs text-gray-500">
              We'll check robots.txt before scraping. Only compliant websites will be scraped.
            </p>
          </div>

          {/* Number of Slides */}
          <div>
            <label htmlFor="num_slides" className="block text-sm font-semibold text-gray-700 mb-2">
              Number of Slides: {formData.num_slides}
            </label>
            <input
              type="range"
              id="num_slides"
              name="num_slides"
              min="3"
              max="15"
              value={formData.num_slides}
              onChange={handleInputChange}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>3</span>
              <span>15</span>
            </div>
          </div>

          {/* Theme Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Theme
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {themes.map(theme => (
                <label
                  key={theme.value}
                  className={`cursor-pointer border-2 rounded-lg p-3 transition-all ${
                    formData.theme === theme.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="theme"
                    value={theme.value}
                    checked={formData.theme === theme.value}
                    onChange={handleInputChange}
                    className="sr-only"
                  />
                  <div className="font-semibold text-gray-900">{theme.label}</div>
                  <div className="text-xs text-gray-600 mt-1">{theme.description}</div>
                </label>
              ))}
            </div>
          </div>

          {/* AI Provider */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              AI Provider
            </label>
            <div className="flex gap-4">
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="ai_provider"
                  value="groq"
                  checked={formData.ai_provider === 'groq'}
                  onChange={handleInputChange}
                  className="mr-2"
                />
                <span className="text-gray-700">Groq (Faster)</span>
              </label>
            </div>
          </div>

          {/* Brand Colors */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Brand Colors (Optional)
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={colorInput}
                onChange={(e) => setColorInput(e.target.value)}
                placeholder="e.g., #FF5733 or 255,87,51"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={handleAddColor}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Add
              </button>
            </div>
            {formData.brand_colors.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.brand_colors.map((color, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 bg-gray-100 px-3 py-1 rounded-full"
                  >
                    <span className="text-sm">{color}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveColor(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Upload Document (Optional)
            </label>
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {uploadedText && (
              <p className="text-xs text-green-600 mt-2">
                ✓ Text extracted ({uploadedText.length} characters)
              </p>
            )}
          </div>

          {/* Source Text */}
          <div>
            <label htmlFor="source_text" className="block text-sm font-semibold text-gray-700 mb-2">
              Additional Context (Optional)
            </label>
            <textarea
              id="source_text"
              name="source_text"
              value={formData.source_text}
              onChange={handleInputChange}
              rows={6}
              placeholder="Paste any text or notes you want to include in the presentation..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Generating...' : 'Generate Presentation'}
          </button>
        </form>
      </div>
    </div>
  )
}
