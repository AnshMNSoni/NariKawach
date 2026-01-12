import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000",
});

export const calculateRisk = async (payload: Record<string, any>) => {

  const response = await api.post("/risk/calculate", payload);
  return response.data;
};
