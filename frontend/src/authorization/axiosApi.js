import axios from "axios";
import { BASE_URL } from "./constants";

export function getHeaderAuthorization() {
  if (
    typeof window !== "undefined" &&
    window.localStorage !== null &&
    window.localStorage !== undefined
  ) {
    return (
      window.localStorage.getItem("token") &&
      `Token ${window.localStorage.getItem("token")}`
    );
  }
}

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 5000,
  headers: {
    Authorization: getHeaderAuthorization(),
    "Content-Type": "application/json",
    accept: "application/json",
  },
});

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      originalRequest.url === BASE_URL + "obtain-token/"
    ) {
      localStorage.clear();
      return Promise.reject(error);
    }

    if (
      error.response?.status === 401 || error.response?.status === 403
    ) {
        localStorage.clear();
        window.location.href = "/login"
    }
    
    return Promise.reject(error);
  }
);

export default axiosInstance;
