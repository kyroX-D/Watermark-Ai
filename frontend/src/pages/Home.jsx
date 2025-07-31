import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Droplets,
  Shield,
  Zap,
  Sparkles,
  Check,
  ArrowRight,
} from "lucide-react";
import Header from "../components/common/Header";

const features = [
  {
    icon: Shield,
    title: "AI-Resistant Protection",
    description:
      "Smart watermarks that blend naturally into your images, making them difficult for AI to remove",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description:
      "Process images in seconds with our optimized AI pipeline powered by Google Gemini",
  },
  {
    icon: Sparkles,
    title: "Intelligent Placement",
    description:
      "AI analyzes your images to find the perfect spot for watermarks - in textures, on walls, or as natural elements",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20" />

        <div className="relative container mx-auto px-4 py-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl mx-auto"
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="bg-gradient-to-r from-primary-600 to-primary-400 bg-clip-text text-transparent">
                Intelligent
              </span>{" "}
              Watermarks
              <br />
              for the AI Era
            </h1>

            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
              Protect your images with AI-powered watermarks that seamlessly
              blend into your content. Smart, secure, and impossible to remove.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="btn-primary text-lg px-8 py-3 inline-flex items-center"
              >
                Get Started Free
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link to="/pricing" className="btn-secondary text-lg px-8 py-3">
                View Pricing
              </Link>
            </div>

            <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
              2 free watermarks daily • No credit card required
            </p>
          </motion.div>

          {/* Floating Elements */}
          <motion.div
            animate={{
              y: [0, -20, 0],
              rotate: [0, 5, 0],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="absolute top-20 right-10 w-20 h-20 bg-primary-200 dark:bg-primary-700 rounded-full blur-3xl opacity-50"
          />
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white dark:bg-dark-surface">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Why Choose AI Watermark?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              State-of-the-art protection for your digital assets
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="card p-6 hover:shadow-xl transition-shadow"
              >
                <feature.icon className="w-12 h-12 text-primary-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Protect Your Images?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Start protecting your work with AI watermarks
          </p>
          <Link
            to="/register"
            className="bg-white text-primary-600 hover:bg-gray-100 font-bold py-3 px-8 rounded-lg inline-flex items-center transition-colors"
          >
            Start Free Trial
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
