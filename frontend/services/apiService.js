const API_CONFIG = {
  baseURL: "<BACKEND_URL>", // Configure the relevant backend url
  headers: {
  "Content-Type": "application/json",
  },
};

// Utility: build full URL
const buildURL = (endpoint) => {
  const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return `${API_CONFIG.baseURL}${path}`;
};

// Generic response handler
const handleResponse = async (response) => {
  if (!response.ok) {
    let errorBody = {};
    try { errorBody = await response.json(); } catch (_) {}
    const message = errorBody?.detail || `HTTP Error: ${response.status} ${response.statusText}`;
    const error = new Error(message);
    error.status = response.status;
    error.body = errorBody;
    throw error;
  }

  if (response.status === 204) return null;
  try { return await response.json(); } catch (_) { return null; }
};

class ApiService {
  // -------------------- Generic Methods --------------------
  static async get(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    const url = `${buildURL(endpoint)}${query ? `?${query}` : ""}`;
    const response = await fetch(url, { method: "GET", headers: API_CONFIG.headers });
    return handleResponse(response);
  }

  static async post(endpoint, data = {}) {
    const response = await fetch(buildURL(endpoint), {
      method: "POST",
      headers: API_CONFIG.headers,
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  }

  static async put(endpoint, data = {}) {
    const response = await fetch(buildURL(endpoint), {
      method: "PUT",
      headers: API_CONFIG.headers,
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  }

  static async delete(endpoint) {
    const response = await fetch(buildURL(endpoint), { method: "DELETE", headers: API_CONFIG.headers });
    return handleResponse(response);
  }

  // -------------------- Product-specific Methods --------------------
  static async fetchAllProducts() {
    return this.get("/products");
  }

  static async getProduct(productId, categoryId) {
    return this.get(`/products/${productId}`, { category_id: categoryId });
  }

  static async createProduct(productData) {
    return this.post("/products", productData);
  }

  static async updateProduct(productData) {
    return this.put("/products", productData);
  }

  static async deleteProduct(productId, categoryId) {
    if (!productId || !categoryId) throw new Error("Missing productId or categoryId");
    return this.delete(`/products/${productId}?category_id=${categoryId}`);
  }

  // -------------------- Streaming Method for Chat --------------------
  static async postWithStream(
    endpoint,
    data = {},
    onChunk = null,
    options = {}
  ) {
    try {
      // Merge default headers with stream-specific headers
      const streamHeaders = {
        ...API_CONFIG.headers,
        Accept: "text/event-stream",
        ...options.headers,
      };

      const response = await fetch(buildURL(endpoint), {
        method: "POST",
        headers: streamHeaders,
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("ReadableStream not supported in this browser.");
      }

      // Get the response reader
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      // Read the stream
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          // Process any remaining data in the buffer
          if (buffer && onChunk) {
            try {
              const jsonData = JSON.parse(buffer);
              await onChunk(jsonData);
            } catch (e) {
              console.warn("Error parsing final chunk:", e);
            }
          }
          break;
        }

        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete JSON objects from the buffer
        while (true) {
          const newlineIndex = buffer.indexOf("\n");
          if (newlineIndex === -1) break;

          const chunk = buffer.slice(0, newlineIndex);
          buffer = buffer.slice(newlineIndex + 1);

          if (chunk.trim() && onChunk) {
            try {
              const data = chunk.slice(6);
              const jsonData = JSON.parse(data);
              await onChunk(jsonData);
            } catch (e) {
              console.warn("Error parsing chunk:", e);
            }
          }
        }
      }

      return { success: true };
    } catch (error) {
      console.error("Streaming POST Request Error:", error);
      throw error;
    }
  }
}



export default ApiService;
