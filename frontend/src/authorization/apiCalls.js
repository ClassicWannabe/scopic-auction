import axiosInstance from "./axiosApi";

export async function getToken(credentials) {
  return await axiosInstance.post("obtain-token/", credentials);
}

export async function getItems(order, page) {
  return await axiosInstance.get("item-list", { params: { order, page } });
}
