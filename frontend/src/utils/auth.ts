export const getUser = () => {
  return JSON.parse(localStorage.getItem("nk_user") || "null");
};
