import { useState } from "react";
import { motion } from "framer-motion";
import { Wand2, Download, Loader } from "lucide-react";
import toast from "react-hot-toast";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import ImageUploader from "../components/watermark/ImageUploader";
import { useAuthStore } from "../hooks/useAuth";
import api from "../services/api";

export default function CreateWatermark() {
  const { token } = useAuthStore();
  const [selectedImage, setSelectedImage] = useState(null);
  const [watermarkText, setWatermarkText] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const handleCreate = async () => {
    if (!selectedImage || !watermarkText.trim()) {
      toast.error("Please select an image and enter watermark text");
      return;
    }

    setIsProcessing(true);
    const formData = new FormData();
    formData.append("image", selectedImage);
    formData.append("watermark_text", watermarkText);

    try {
      const response = await api.post("/watermarks/create", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      setResult(response.data);
      toast.success("Watermark created successfully!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create watermark");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;

    const link = document.createElement("a");
    link.href = `${import.meta.env.VITE_API_URL}${result.watermarked_image_url}`;
    link.download = `watermarked_${Date.now()}.png`;
    link.click();
  };

  const resetForm = () => {
    setSelectedImage(null);
    setWatermarkText("");
    setResult(null);
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Create AI-Powered Watermark</h1>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            <div className="card p-6">
              <h2 className="text-xl font-semibold mb-4">
                1. Upload Your Image
              </h2>
              <ImageUploader onImageSelect={setSelectedImage} />
            </div>

            <div className="card p-6">
              <h2 className="text-xl font-semibold mb-4">
                2. Enter Watermark Text
              </h2>
              <input
                type="text"
                placeholder="Your watermark text..."
                className="input-field"
                value={watermarkText}
                onChange={(e) => setWatermarkText(e.target.value)}
                maxLength={50}
              />
              <p className="text-sm text-gray-500 mt-2">
                {watermarkText.length}/50 characters
              </p>
            </div>

            <button
              onClick={handleCreate}
              disabled={!selectedImage || !watermarkText.trim() || isProcessing}
              className="w-full btn-primary py-3 flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  <span>Create Watermark</span>
                </>
              )}
            </button>
          </div>

          {/* Preview Section */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4">Preview</h2>

            {result ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-4"
              >
                <div className="relative rounded-lg overflow-hidden bg-gray-100 dark:bg-dark-bg">
                  <img
                    src={`${import.meta.env.VITE_API_URL}${result.watermarked_image_url}`}
                    alt="Watermarked"
                    className="w-full h-auto"
                  />
                </div>

                <div className="flex space-x-4">
                  <button
                    onClick={handleDownload}
                    className="flex-1 btn-primary py-2 flex items-center justify-center space-x-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </button>
                  <button
                    onClick={resetForm}
                    className="flex-1 btn-secondary py-2"
                  >
                    Create Another
                  </button>
                </div>

                {result.ai_analysis && (
                  <div className="mt-4 p-4 bg-gray-50 dark:bg-dark-bg rounded-lg">
                    <h3 className="font-semibold mb-2">AI Analysis</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {result.ai_analysis.scene_description}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                      Processing time: {result.processing_time}ms
                    </p>
                  </div>
                )}
              </motion.div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400">
                <p>Your watermarked image will appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
