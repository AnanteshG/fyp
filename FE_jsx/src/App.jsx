import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { SignIn, SignUp } from '@clerk/clerk-react'
import Layout from './components/Layout'
import Home from './pages/Home'
import Generate from './pages/Generate'
import Editor from './pages/Editor'
import History from './pages/History'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="generate" element={<Generate />} />
          <Route path="editor/:pptId" element={<Editor />} />
          <Route path="history" element={<History />} />
          <Route 
            path="sign-in/*" 
            element={
              <div className="flex items-center justify-center min-h-screen">
                <SignIn routing="path" path="/sign-in" />
              </div>
            } 
          />
          <Route 
            path="sign-up/*" 
            element={
              <div className="flex items-center justify-center min-h-screen">
                <SignUp routing="path" path="/sign-up" />
              </div>
            } 
          />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
