import { useState } from 'react'

export default function SlidePreview({ slide, slideIndex, onUpdate, onImageChange }) {
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const [editedTitle, setEditedTitle] = useState(slide.title || '')
  const [editedBullets, setEditedBullets] = useState(slide.content || [])
  const [showImagePicker, setShowImagePicker] = useState(false)
  const [imageError, setImageError] = useState(false)

  // Use Firebase URL if available, otherwise fall back to image_path
  const imageUrl = slide.image_firebase_url || slide.image_path

  const handleTitleSave = () => {
    if (editedTitle !== slide.title) {
      onUpdate(slideIndex, { ...slide, title: editedTitle })
    }
    setIsEditingTitle(false)
  }

  const handleBulletChange = (bulletIndex, newValue) => {
    const newBullets = [...editedBullets]
    newBullets[bulletIndex] = newValue
    setEditedBullets(newBullets)
  }

  const handleBulletSave = () => {
    if (JSON.stringify(editedBullets) !== JSON.stringify(slide.content)) {
      onUpdate(slideIndex, { ...slide, content: editedBullets })
    }
  }

  const handleImageSelect = (imageUrl) => {
    onImageChange(slideIndex, imageUrl)
    setShowImagePicker(false)
    setImageError(false) // Reset error state when new image is selected
  }

  console.log(slide)

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
      {/* Title Section */}
      <div className="mb-6 pb-6 border-b border-gray-200">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            {isEditingTitle ? (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={editedTitle}
                  onChange={(e) => setEditedTitle(e.target.value)}
                  className="flex-1 px-4 py-3 text-2xl font-bold border-2 border-blue-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                  placeholder="Enter slide title..."
                />
                <button
                  onClick={handleTitleSave}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setEditedTitle(slide.title || '')
                    setIsEditingTitle(false)
                  }}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <h3
                  className="text-3xl font-bold text-gray-900 cursor-pointer hover:text-blue-600 transition-colors"
                  onClick={() => setIsEditingTitle(true)}
                  title="Click to edit"
                >
                  {slide.title || 'Untitled Slide'}
                </h3>
                <button
                  onClick={() => setIsEditingTitle(true)}
                  className="text-gray-400 hover:text-blue-600 transition-colors"
                  title="Edit title"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Content Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h4 className="text-lg font-semibold text-gray-900">Content</h4>
          </div>

          <ul className="space-y-3">
            {editedBullets.map((bullet, idx) => (
              <li key={idx} className="flex items-start gap-3 group">
                <div className="flex-shrink-0 w-2 h-2 mt-2 rounded-full bg-blue-600"></div>
                <input
                  type="text"
                  value={bullet}
                  onChange={(e) => handleBulletChange(idx, e.target.value)}
                  onBlur={() => handleBulletSave()}
                  className="flex-1 px-3 py-2 text-gray-700 bg-gray-50 border border-gray-200 rounded-lg hover:border-blue-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
                  placeholder={`Bullet point ${idx + 1}...`}
                />
              </li>
            ))}
          </ul>

          {slide.speaker_notes && (
            <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-start gap-2 mb-2">
                <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
                <h5 className="text-sm font-semibold text-amber-900">Speaker Notes</h5>
              </div>
              <p className="text-sm text-amber-900 leading-relaxed pl-7">{slide.speaker_notes}</p>
            </div>
          )}
        </div>

        {/* Image Section */}
        <div className="space-y-4">
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h4 className="text-lg font-semibold text-gray-900">Image</h4>
            </div>
            {/* <button
              onClick={() => setShowImagePicker(!showImagePicker)}
              className="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors font-medium"
            >
              {slide.image_path ? '🔄 Change' : '➕ Add Image'}
            </button> */}
          </div>

          {slide.image_path ? (
            <div className="relative group">
              {!imageError ? (
                <img
                  src={imageUrl}
                  alt={slide.title || 'Slide image'}
                  className="w-full h-64 object-cover rounded-lg shadow-md border border-gray-200"
                  onError={() => setImageError(true)}
                  crossOrigin="anonymous"
                />
              ) : (
                <div className="w-full h-64 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-300">
                  <div className="text-center p-4">
                    <svg className="mx-auto h-16 w-16 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="mt-3 text-sm font-medium">Image unavailable</p>
                    <p className="mt-1 text-xs">Select a new image below</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="w-full h-64 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-300">
              <div className="text-center p-4">
                <svg className="mx-auto h-16 w-16 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="mt-3 text-sm font-medium">No image</p>
                <p className="mt-1 text-xs">Click "Add Image" to select one</p>
              </div>
            </div>
          )}

          {showImagePicker && slide.suggested_images && slide.suggested_images.length > 0 && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h5 className="text-sm font-semibold text-gray-900 mb-3">Suggested Images</h5>
              <div className="grid grid-cols-2 gap-3">
                {slide.suggested_images.map((img, idx) => (
                  <div
                    key={idx}
                    className="relative group cursor-pointer overflow-hidden rounded-lg border-2 border-gray-200 hover:border-blue-500 transition-all"
                    onClick={() => handleImageSelect(img.largeImageURL || img.url)}
                  >
                    <img
                      src={img.webformatURL || img.largeImageURL || img.url}
                      alt={`Suggestion ${idx + 1}`}
                      className="w-full h-24 object-cover group-hover:scale-110 transition-transform duration-200"
                    />
                    <div className="absolute inset-0 bg-blue-600 bg-opacity-0 group-hover:bg-opacity-20 transition-opacity flex items-center justify-center">
                      <svg className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
