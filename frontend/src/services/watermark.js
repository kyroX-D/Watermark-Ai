// File: frontend/src/services/watermark.js

import api from "./api";

export const watermarkService = {
  create: async (image, watermarkText, customSettings = {}) => {
    const formData = new FormData();
    formData.append("image", image);
    formData.append("watermark_text", watermarkText);
    
    // Position and basic settings
    formData.append("text_position", customSettings.position || "bottom-right");
    formData.append("text_size", customSettings.size || "medium");
    formData.append("text_opacity", customSettings.opacity || 0.7);
    
    // Auto features
    formData.append("auto_opacity", customSettings.autoOpacity || false);
    
    // Multiple watermarks
    formData.append("multiple_watermarks", customSettings.multipleWatermarks || false);
    if (customSettings.multipleWatermarks) {
      formData.append("watermark_pattern", customSettings.pattern || "diagonal");
    }
    
    // Font and styling
    if (customSettings.fontFamily) {
      formData.append("font_family", customSettings.fontFamily);
    }
    if (customSettings.textColor) {
      formData.append("text_color", customSettings.textColor);
    }
    if (customSettings.textShadow !== undefined) {
      formData.append("text_shadow", customSettings.textShadow);
    }
    
    // Protection mode
    formData.append("protection_mode", customSettings.protectionMode || "standard");

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
  
  getAvailableFonts: async () => {
    const response = await api.get("/watermarks/fonts");
    return response.data;
  }
};