export const validators = {
  email: (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  password: (password) => {
    if (password.length < 8) {
      return "Password must be at least 8 characters long";
    }
    if (!/\d/.test(password)) {
      return "Password must contain at least one number";
    }
    if (!/[A-Z]/.test(password)) {
      return "Password must contain at least one uppercase letter";
    }
    return null;
  },

  username: (username) => {
    if (username.length < 3) {
      return "Username must be at least 3 characters long";
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      return "Username can only contain letters, numbers, underscores, and hyphens";
    }
    return null;
  },

  watermarkText: (text) => {
    if (!text || !text.trim()) {
      return "Watermark text cannot be empty";
    }
    if (text.length > 50) {
      return "Watermark text must be 50 characters or less";
    }
    return null;
  },

  imageFile: (file) => {
    if (!file) {
      return "Please select an image";
    }
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      return "Invalid file type. Please upload JPEG, PNG or WebP";
    }
    if (file.size > 10 * 1024 * 1024) {
      return "File size must be less than 10MB";
    }
    return null;
  },
};
