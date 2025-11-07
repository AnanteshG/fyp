import axios from "axios";

const API_BASE = "/api/v1";

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE,
});

// Add interceptor to include auth token from localStorage
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data on 401
      localStorage.removeItem("authToken");
      // Optionally redirect to login
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// Legacy function for compatibility
export function setAuthToken(token) {
  if (token) {
    apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("authToken", token);
  } else {
    delete apiClient.defaults.headers.common["Authorization"];
    localStorage.removeItem("authToken");
  }
}

// Generate a new presentation
export async function generatePPT(data) {
  const response = await apiClient.post("/generate", data);
  return response.data;
}

// Get presentation metadata
export async function getPPTMetadata(pptId) {
  const response = await apiClient.get(`/ppt/${pptId}`);
  return response.data;
}

// Download presentation file
export async function downloadPPT(pptId) {
  const response = await apiClient.get(`/download/${pptId}`, {
    responseType: "blob",
  });
  return response.data;
}

// Delete presentation
export async function deletePPT(pptId) {
  const response = await apiClient.delete(`/ppt/${pptId}`);
  return response.data;
}

// Update a specific slide
export async function updateSlide(pptId, slideIndex, slideData) {
  const response = await apiClient.patch(
    `/ppt/${pptId}/slide/${slideIndex}`,
    slideData
  );
  return response.data;
}

// Replace image in a slide
export async function replaceImage(data) {
  const response = await apiClient.post("/replace-image", data);
  return response.data;
}

// Search for images on Pixabay
export async function searchPixabayImages(query, page = 1, perPage = 20) {
  const response = await apiClient.get("/pixabay/search", {
    params: { q: query, page, per_page: perPage },
  });
  return response.data;
}

// Upload source document
export async function uploadSource(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post("/upload-source", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
}

// Check robots.txt for a URL
export async function checkRobots(url) {
  const response = await apiClient.get("/robots-check", {
    params: { url },
  });
  return response.data;
}

// Check multiple URLs for robots.txt compliance
export async function checkMultipleUrls(urls) {
  const results = await Promise.all(
    urls.map(async (url) => {
      try {
        const result = await checkRobots(url);
        return { url, ...result };
      } catch (error) {
        return {
          url,
          allowed: false,
          message: error.response?.data?.error || "Failed to check URL",
        };
      }
    })
  );
  return results;
}

// Get user's presentation history
export async function getHistory(limit = 50) {
  const response = await apiClient.get("/history", {
    params: { limit },
  });
  return response.data;
}

// Get current user info
export async function getUserInfo() {
  const response = await apiClient.get("/user/info");
  return response.data;
}
