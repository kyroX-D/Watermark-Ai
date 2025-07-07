export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login",
    REGISTER: "/auth/register",
    GOOGLE: "/auth/google",
    GOOGLE_CALLBACK: "/auth/google/callback",
  },
  USERS: {
    ME: "/users/me",
    STATS: "/users/stats",
    UPDATE: "/users/me",
    CHANGE_PASSWORD: "/users/change-password",
    DELETE: "/users/me",
  },
  WATERMARKS: {
    CREATE: "/watermarks/create",
    LIST: "/watermarks/my-watermarks",
    DELETE: "/watermarks/:id",
  },
  SUBSCRIPTIONS: {
    CREATE_CHECKOUT: "/subscriptions/create-checkout",
    CREATE_CRYPTO: "/subscriptions/create-crypto-payment",
    CURRENT: "/subscriptions/current",
    CANCEL: "/subscriptions/cancel",
  },
};

export const SUBSCRIPTION_TIERS = {
  FREE: {
    name: "Free",
    dailyLimit: 2,
    maxResolution: 720,
    features: ["Basic watermarks", "Standard processing"],
  },
  PRO: {
    name: "Pro",
    price: 20,
    dailyLimit: null,
    maxResolution: 1080,
    features: ["Unlimited watermarks", "Premium styles", "Priority processing"],
  },
  ELITE: {
    name: "Elite",
    price: 50,
    dailyLimit: null,
    maxResolution: 2160,
    features: [
      "4K resolution",
      "Exclusive styles",
      "API access",
      "Priority support",
    ],
  },
};

export const IMAGE_FORMATS = {
  ACCEPTED: ["image/jpeg", "image/png", "image/webp"],
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
};
