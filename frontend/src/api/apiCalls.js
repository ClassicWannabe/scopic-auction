import axiosInstance from "./axiosApi";

export async function getToken(credentials) {
  return await axiosInstance.post("obtain-token/", credentials);
}

export async function getItems(filter, page) {
  return await axiosInstance.get("items/", { params: { ...filter, page } });
}

export async function getSpecificItem(id) {
  return await axiosInstance.get(`items/${id}`);
}

export async function getBid(id) {
  return await axiosInstance.get(`bids/${id}`);
}

export async function getOwnBid(auction_item) {
  return await axiosInstance.get(`bids/own-bid`, { params: { auction_item } });
}

export async function makeBid(data, { id = null, create = false } = {}) {
  if (create) {
    return await axiosInstance.post(`bids/`, data);
  }
  if (id) {
    return await axiosInstance.patch(`bids/${id}/`, data);
  }
}

export async function getUserDetails(token) {
  return await axiosInstance.get("user/", {
    headers: { Authorization: `Token ${token}` },
  });
}

export async function updateUserDetails(data) {
  return await axiosInstance.patch("user/", data);
}
