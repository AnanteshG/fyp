import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getPPTMetadata, updateSlide, replaceImage, downloadPPT, searchPixabayImages } from '../api'
import SlidePreview from '../components/SlidePreview'

export default function Editor() {
  const { pptId } = useParams()
  const navigate = useNavigate()

  const [presentation, setPresentation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [downloading, setDownloading] = useState(false)
  const [showImageSearch, setShowImageSearch] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [activeSlideForImage, setActiveSlideForImage] = useState(null)
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0)

  useEffect(() => {
    loadPresentation()
  }, [pptId])

  const loadPresentation = async () => {
    try {
      const data = await getPPTMetadata(pptId)
      setPresentation(data)
      setLoading(false)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load presentation')
      setLoading(false)
    }
  }

  const handleSlideUpdate = async (slideIndex, updatedSlide) => {
    try {
      const result = await updateSlide(pptId, slideIndex, updatedSlide)
      setPresentation(result)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update slide')
    }
  }

  const handleImageChange = async (slideIndex, imageUrl) => {
    try {
      const result = await replaceImage({
        ppt_id: pptId,
        slide_index: slideIndex,
        new_image_url: imageUrl
      })
      setPresentation(result)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to replace image')
    }
  }

  const handleOpenImageSearch = (slideIndex) => {
    setActiveSlideForImage(slideIndex)
    const slide = presentation.slides[slideIndex]
    setSearchQuery(slide.title || '')
    setShowImageSearch(true)
  }

  const handleImageSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    try {
      const results = await searchPixabayImages(searchQuery)
      setSearchResults(results.images || [])
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to search images')
    }
  }

  const handleSelectSearchedImage = async (imageUrl) => {
    await handleImageChange(activeSlideForImage, imageUrl)
    setShowImageSearch(false)
    setSearchResults([])
    setActiveSlideForImage(null)
  }

  const handleDownload = async () => {
    setDownloading(true)
    try {
      const blob = await downloadPPT(pptId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${presentation.topic.replace(/\s+/g, '_')}.pptx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to download presentation')
    } finally {
      setDownloading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading presentation...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-12">
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
          <h3 className="font-semibold mb-2">Error</h3>
          <p>{error}</p>
          <button
            onClick={() => navigate('/generate')}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
          >
            Generate New Presentation
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar - Slide Navigation */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col shadow-sm">
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 mb-1 truncate" title={presentation.topic}>
            {presentation.topic}
          </h2>
          <p className="text-sm text-gray-500">
            <span className="font-semibold">{presentation.theme}</span> • {presentation.slides.length} slides
          </p>
        </div>

        {/* Slide Thumbnails */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {presentation.slides.map((slide, index) => (
            <div
              key={index}
              onClick={() => setCurrentSlideIndex(index)}
              className={`cursor-pointer rounded-lg border-2 transition-all duration-200 ${currentSlideIndex === index
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : 'border-gray-200 hover:border-blue-300 hover:shadow-sm bg-white'
                }`}
            >
              <div className="p-3">
                <div className="flex items-start gap-3">
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${currentSlideIndex === index
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-600'
                    }`}>
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-gray-900 truncate mb-1">
                      {slide.title || 'Untitled Slide'}
                    </h3>
                    <p className="text-xs text-gray-500 line-clamp-2">
                      {slide.content && slide.content.length > 0
                        ? slide.content[0]
                        : 'No content'}
                    </p>
                  </div>
                </div>
                {slide.image_path && (
                  <div className="mt-2 rounded overflow-hidden">
                    <img
                      src={slide.image_path}
                      alt={slide.title}
                      className="w-full h-16 object-cover"
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Sidebar Footer - Actions */}
        <div className="p-4 border-t border-gray-200 space-y-2">
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors flex items-center justify-center gap-2"
          >
            {downloading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Downloading...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download PPTX
              </>
            )}
          </button>
          <button
            onClick={() => navigate('/generate')}
            className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
          >
            New Presentation
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-8">
          {/* Current Slide Header */}
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-1">
                Slide {currentSlideIndex + 1} of {presentation.slides.length}
              </h1>
              <p className="text-gray-600">
                Edit your slide content, images, and speaker notes below
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
                disabled={currentSlideIndex === 0}
                className="p-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                title="Previous slide"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button
                onClick={() => setCurrentSlideIndex(Math.min(presentation.slides.length - 1, currentSlideIndex + 1))}
                disabled={currentSlideIndex === presentation.slides.length - 1}
                className="p-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                title="Next slide"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          {/* Slide Preview Component */}
          <SlidePreview
            slide={presentation.slides[currentSlideIndex]}
            slideIndex={currentSlideIndex}
            onUpdate={handleSlideUpdate}
            onImageChange={handleImageChange}
          />
        </div>
      </div>

      {/* Image Search Modal */}
      {showImageSearch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-gray-900">Search Images</h2>
                <button
                  onClick={() => {
                    setShowImageSearch(false)
                    setSearchResults([])
                  }}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              <form onSubmit={handleImageSearch} className="mb-6">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search for images..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="submit"
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Search
                  </button>
                </div>
              </form>

              {searchResults.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {searchResults.map((img, idx) => (
                    <div
                      key={idx}
                      className="cursor-pointer hover:opacity-75 transition-opacity"
                      onClick={() => handleSelectSearchedImage(img.largeImageURL)}
                    >
                      <img
                        src={img.previewURL}
                        alt={img.tags}
                        className="w-full h-48 object-cover rounded-lg shadow-md"
                      />
                      <p className="text-xs text-gray-600 mt-2 truncate">{img.tags}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
