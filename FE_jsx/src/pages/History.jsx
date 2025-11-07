import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getHistory, deletePPT } from '../api'
import { useAuth } from '../contexts/AuthContext'

export default function History() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [presentations, setPresentations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadPresentations()
  }, [user])

  const loadPresentations = async () => {
    try {
      setLoading(true)
      const data = await getHistory(50)
      setPresentations(data.presentations || [])
      setError('')
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load presentations')
      console.error('Error loading presentations:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleView = (pptId) => {
    navigate(`/editor/${pptId}`)
  }

  const handleDelete = async (pptId) => {
    if (window.confirm('Are you sure you want to delete this presentation?')) {
      try {
        await deletePPT(pptId)
        setPresentations(presentations.filter(p => p.ppt_id !== pptId))
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete presentation')
      }
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your presentations...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg mb-4">
            <h3 className="font-semibold mb-2">Error</h3>
            <p>{error}</p>
          </div>
          <button
            onClick={() => navigate('/generate')}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700"
          >
            Create Presentation
          </button>
        </div>
      </div>
    )
  }

  if (presentations.length === 0) {
    return (
      <div className="px-4 py-12">
        <div className="max-w-3xl mx-auto text-center">
          <div className="text-6xl mb-4">📊</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">No Presentations Yet</h1>
          <p className="text-gray-600 mb-8">
            You haven't created any presentations yet. Start by generating your first one!
          </p>
          <button
            onClick={() => navigate('/generate')}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700"
          >
            Create Presentation
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Presentation History</h1>
        <p className="text-gray-600 mb-8">{presentations.length} presentation{presentations.length !== 1 ? 's' : ''} found</p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {presentations.map((ppt) => (
            <div key={ppt.ppt_id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              {/* Thumbnail */}
              {ppt.thumbnail && (
                <div className="relative h-40 bg-gray-100 overflow-hidden">
                  <img
                    src={ppt.thumbnail}
                    alt={ppt.topic}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              {/* Content */}
              <div className="p-4">
                <h3 className="text-lg font-bold text-gray-900 mb-2 truncate" title={ppt.topic}>
                  {ppt.topic}
                </h3>
                <div className="space-y-1 text-sm text-gray-600 mb-4">
                  <p>Theme: <span className="font-semibold capitalize">{ppt.theme}</span></p>
                  <p>Slides: <span className="font-semibold">{ppt.slide_count}</span></p>
                  {ppt.created_at && (
                    <p>Created: <span className="font-semibold">{new Date(ppt.created_at.toDate?.() || ppt.created_at).toLocaleDateString()}</span></p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => handleView(ppt.ppt_id)}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(ppt.ppt_id)}
                    className="px-4 py-2 border border-red-300 text-red-600 rounded-md hover:bg-red-50 transition-colors text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
