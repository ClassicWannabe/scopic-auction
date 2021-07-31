import axiosInstance from "./axiosApi";

export async function getToken(credentials) {
  return await axiosInstance.post("obtain-token/", credentials);
}

export async function getItems(filter, page) {
  return await axiosInstance.get("items/", { params: { ...filter, page } });
}

export async function getUserDetails(token) {
  return await axiosInstance.get("user-detail/", {
    headers: { Authorization: `Token ${token}` },
  });
}
