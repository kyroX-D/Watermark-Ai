import { create } from "zustand";
import { subscriptionService } from "../services/subscription";

export const useSubscriptionStore = create((set, get) => ({
  subscription: null,
  loading: false,
  error: null,

  fetchSubscription: async () => {
    set({ loading: true, error: null });
    try {
      const data = await subscriptionService.getCurrentSubscription();
      set({ subscription: data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  createCheckout: async (priceId) => {
    set({ loading: true, error: null });
    try {
      const successUrl = `${window.location.origin}/dashboard?subscription=success`;
      const cancelUrl = `${window.location.origin}/pricing`;

      const session = await subscriptionService.createStripeCheckout(
        priceId,
        successUrl,
        cancelUrl,
      );

      await subscriptionService.redirectToStripeCheckout(session.session_id);
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  createCryptoPayment: async (planId, amount, currency) => {
    set({ loading: true, error: null });
    try {
      const payment = await subscriptionService.createCryptoPayment(
        planId,
        amount,
        currency,
      );

      window.location.href = payment.payment_url;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },

  cancelSubscription: async () => {
    set({ loading: true, error: null });
    try {
      await subscriptionService.cancelSubscription();
      await get().fetchSubscription();
      return true;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
}));
