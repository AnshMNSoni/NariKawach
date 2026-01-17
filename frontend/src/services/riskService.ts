import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL;

if (!API_BASE_URL) {
  throw new Error("VITE_API_URL is not defined");
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const calculateRisk = async (payload: Record<string, any>) => {
  const response = await api.post("/risk/calculate", payload);
  return response.data;
};
