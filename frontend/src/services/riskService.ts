import { api } from "@/lib/api";

export const calculateRisk = async (payload: Record<string, any>) => {
  const response = await api.post("/risk/calculate", payload);
  return response.data;
};
