import api from "./api";
import { loadStripe } from "@stripe/stripe-js";

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);

export const subscriptionService = {
  createStripeCheckout: async (priceId, successUrl, cancelUrl) => {
    const response = await api.post("/subscriptions/create-checkout", {
      price_id: priceId,
      success_url: successUrl,
      cancel_url: cancelUrl,
    });
    return response.data;
  },

  createCryptoPayment: async (planId, amount, currency = "USDT") => {
    const response = await api.post("/subscriptions/create-crypto-payment", {
      plan_id: planId,
      amount,
      currency,
    });
    return response.data;
  },

  getCurrentSubscription: async () => {
    const response = await api.get("/subscriptions/current");
    return response.data;
  },

  cancelSubscription: async () => {
    const response = await api.post("/subscriptions/cancel");
    return response.data;
  },

  redirectToStripeCheckout: async (sessionId) => {
    const stripe = await stripePromise;
    const { error } = await stripe.redirectToCheckout({ sessionId });

    if (error) {
      throw new Error(error.message);
    }
  },
};
