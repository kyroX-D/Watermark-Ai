import api from "./api";

export const watermarkService = {
  create: async (image, watermarkText) => {
    const formData = new FormData();
    formData.append("image", image);
    formData.append("watermark_text", watermarkText);

    const response = await api.post("/watermarks/create", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  getMyWatermarks: async (skip = 0, limit = 20) => {
    const response = await api.get("/watermarks/my-watermarks", {
      params: { skip, limit },
    });
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/watermarks/${id}`);
    return response.data;
  },
};
