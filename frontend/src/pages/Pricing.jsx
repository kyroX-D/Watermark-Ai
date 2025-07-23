import { useState } from "react";
import { motion } from "framer-motion";
import { Check, Sparkles, Zap, Crown, Loader } from "lucide-react";
import { loadStripe } from "@stripe/stripe-js";
import Header from "../components/common/Header";
import { useAuthStore } from "../hooks/useAuth";
import api from "../services/api";
import toast from "react-hot-toast";

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);

const plans = [
  {
    id: "free",
    name: "Free",
    price: "€0",
    period: "forever",
    icon: Sparkles,
    features: [
      "2 watermarks per day",
      "720p resolution",
      "Basic watermark styles",
      "Standard processing",
      "Email support",
    ],
    limitations: ["Daily limit", "Lower resolution", "Basic features only"],
  },
  {
    id: "pro",
    name: "Pro",
    price: "€20",
    period: "per month",
    icon: Zap,
    popular: true,
    features: [
      "Unlimited watermarks",
      "1080p Full HD resolution",
      "Premium watermark styles",
      "Priority processing",
      "Advanced AI placement",
      "Email & chat support",
      "Bulk processing",
    ],
    stripePrice: "price_pro_id",
  },
  {
    id: "elite",
    name: "Elite",
    price: "€120",
    period: "per month",
    icon: Crown,
    features: [
      "Everything in Pro",
      "4K Ultra HD resolution",
      "Exclusive watermark styles",
      "Fastest processing",
      "Custom watermark designs",
      "API access",
      "Priority support",
      "Advanced analytics",
    ],
    stripePrice: "price_elite_id",
  },
];

export default function Pricing() {
  const { isAuthenticated, token, user } = useAuthStore();
  const [loading, setLoading] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState("stripe");

  const handleSubscribe = async (plan) => {
    if (!isAuthenticated) {
      toast.error("Please login to subscribe");
      window.location.href = "/login";
      return;
    }

    if (plan.id === "free") return;

    setLoading(plan.id);

    try {
      if (paymentMethod === "stripe") {
        const response = await api.post(
          "/subscriptions/create-checkout",
          {
            price_id: plan.stripePrice,
            success_url: `${window.location.origin}/dashboard?subscription=success`,
            cancel_url: `${window.location.origin}/pricing`,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          },
        );

        const stripe = await stripePromise;
        const { error } = await stripe.redirectToCheckout({
          sessionId: response.data.session_id,
        });

        if (error) {
          toast.error(error.message);
        }
      } else {
        // OxaPay
        const response = await api.post(
          "/subscriptions/create-crypto-payment",
          {
            plan_id: plan.id,
            amount: parseInt(plan.price.replace("€", "")),
            currency: "USDT",
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          },
        );

        window.location.href = response.data.payment_url;
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Payment failed");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
      <Header />

      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Start free, upgrade when you need more
          </p>
        </motion.div>

        {/* Payment Method Toggle */}
        {isAuthenticated && (
          <div className="flex justify-center mb-8">
            <div className="bg-white dark:bg-dark-surface rounded-lg p-1 shadow-lg">
              <button
                onClick={() => setPaymentMethod("stripe")}
                className={`px-6 py-2 rounded-md transition-colors ${
                  paymentMethod === "stripe"
                    ? "bg-primary-600 text-white"
                    : "text-gray-600 dark:text-gray-400"
                }`}
              >
                💳 Card Payment
              </button>
              <button
                onClick={() => setPaymentMethod("crypto")}
                className={`px-6 py-2 rounded-md transition-colors ${
                  paymentMethod === "crypto"
                    ? "bg-primary-600 text-white"
                    : "text-gray-600 dark:text-gray-400"
                }`}
              >
                🪙 Crypto (USDT/ETH)
              </button>
            </div>
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => {
            const Icon = plan.icon;
            const isCurrentPlan = user?.subscription_tier === plan.id;

            return (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`
                  relative card p-8 
                  ${plan.popular ? "ring-2 ring-primary-500 scale-105" : ""}
                `}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-primary-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="text-center mb-6">
                  <Icon
                    className={`w-12 h-12 mx-auto mb-4 ${
                      plan.popular
                        ? "text-primary-600"
                        : "text-gray-600 dark:text-gray-400"
                    }`}
                  />
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="text-4xl font-bold mb-1">
                    {plan.price}
                    {plan.period !== "forever" && (
                      <span className="text-lg text-gray-600 dark:text-gray-400">
                        /{plan.period}
                      </span>
                    )}
                  </div>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                  {plan.limitations?.map((limitation) => (
                    <li
                      key={limitation}
                      className="flex items-start opacity-60"
                    >
                      <span className="w-5 h-5 mr-2 flex-shrink-0 text-center">
                        ×
                      </span>
                      <span className="text-sm">{limitation}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleSubscribe(plan)}
                  disabled={loading === plan.id || isCurrentPlan}
                  className={`
                    w-full py-3 rounded-lg font-medium transition-all
                    ${
                      isCurrentPlan
                        ? "bg-gray-200 dark:bg-dark-border text-gray-500 cursor-not-allowed"
                        : plan.popular
                          ? "btn-primary"
                          : "btn-secondary"
                    }
                    flex items-center justify-center
                  `}
                >
                  {loading === plan.id ? (
                    <Loader className="w-5 h-5 animate-spin" />
                  ) : isCurrentPlan ? (
                    "Current Plan"
                  ) : plan.id === "free" ? (
                    "Get Started"
                  ) : (
                    `Subscribe to ${plan.name}`
                  )}
                </button>
              </motion.div>
            );
          })}
        </div>

        <div className="mt-12 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>
            All plans include automatic renewal. Cancel anytime from your
            dashboard.
          </p>
          <p className="mt-2">Prices exclude VAT where applicable.</p>
        </div>
      </div>
    </div>
  );
}
