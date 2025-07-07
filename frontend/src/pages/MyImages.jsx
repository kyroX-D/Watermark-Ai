import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Download, Trash2, Loader, Search } from "lucide-react";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import { useAuthStore } from "../hooks/useAuth";
import api from "../services/api";
import toast from "react-hot-toast";

export default function MyImages() {
  const { token } = useAuthStore();
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      const response = await api.get("/watermarks/my-watermarks", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setImages(response.data);
    } catch (error) {
      toast.error("Failed to load images");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Are you sure you want to delete this watermark?")) return;

    try {
      await api.delete(`/watermarks/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setImages(images.filter((img) => img.id !== id));
      toast.success("Image deleted successfully");
    } catch (error) {
      toast.error("Failed to delete image");
    }
  };

  const handleDownload = (url, filename) => {
    const link = document.createElement("a");
    link.href = `${import.meta.env.VITE_API_URL}${url}`;
    link.download = filename || "watermarked.png";
    link.click();
  };

  const filteredImages = images.filter((img) =>
    img.watermark_text.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <DashboardLayout>
      <div>
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">My Watermarked Images</h1>

          <div className="relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by watermark text..."
              className="input-field pl-10 w-64"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : filteredImages.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              {searchTerm
                ? "No images found matching your search."
                : "No watermarked images yet."}
            </p>
            <a href="/create" className="btn-primary">
              Create Your First Watermark
            </a>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence>
              {filteredImages.map((image, index) => (
                <motion.div
                  key={image.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.05 }}
                  className="card overflow-hidden group"
                >
                  <div
                    className="relative h-48 bg-gray-100 dark:bg-dark-bg cursor-pointer"
                    onClick={() => setSelectedImage(image)}
                  >
                    <img
                      src={`${import.meta.env.VITE_API_URL}${image.watermarked_image_url}`}
                      alt={image.watermark_text}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <p className="text-white text-sm">Click to view</p>
                    </div>
                  </div>

                  <div className="p-4">
                    <p className="font-semibold truncate">
                      {image.watermark_text}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(image.created_at).toLocaleDateString()}
                    </p>

                    <div className="flex space-x-2 mt-4">
                      <button
                        onClick={() =>
                          handleDownload(
                            image.watermarked_image_url,
                            `${image.watermark_text}.png`,
                          )
                        }
                        className="flex-1 btn-primary py-2 text-sm flex items-center justify-center"
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </button>
                      <button
                        onClick={() => handleDelete(image.id)}
                        className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        {/* Image Modal */}
        {selectedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
            onClick={() => setSelectedImage(null)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              className="max-w-4xl max-h-[90vh] relative"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={`${import.meta.env.VITE_API_URL}${selectedImage.watermarked_image_url}`}
                alt={selectedImage.watermark_text}
                className="w-full h-auto max-h-[80vh] object-contain rounded-lg"
              />
              <button
                onClick={() => setSelectedImage(null)}
                className="absolute top-4 right-4 p-2 bg-white/20 backdrop-blur-sm rounded-lg text-white hover:bg-white/30 transition-colors"
              >
                ✕
              </button>
            </motion.div>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
}
