import axios from "axios";
import { API_CONFIG } from "../config/constants.js";

const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: API_CONFIG.HEADERS,
  timeout: API_CONFIG.TIMEOUT,
});

export default api;
