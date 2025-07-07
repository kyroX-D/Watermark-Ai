import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, Image as ImageIcon } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";

export default function ImageUploader({
  onImageSelect,
  maxSize = 10 * 1024 * 1024,
}) {
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);

  const onDrop = useCallback(
    (acceptedFiles, rejectedFiles) => {
      if (rejectedFiles.length > 0) {
        const error = rejectedFiles[0].errors[0];
        if (error.code === "file-too-large") {
          toast.error(
            `File too large. Maximum size is ${maxSize / 1024 / 1024}MB`,
          );
        } else if (error.code === "file-invalid-type") {
          toast.error("Invalid file type. Please upload JPEG, PNG or WebP");
        }
        return;
      }

      const file = acceptedFiles[0];
      setFile(file);

      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result);
        onImageSelect(file);
      };
      reader.readAsDataURL(file);
    },
    [onImageSelect, maxSize],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "image/webp": [".webp"],
    },
    maxSize,
    multiple: false,
  });

  const removeImage = () => {
    setPreview(null);
    setFile(null);
    onImageSelect(null);
  };

  return (
    <div className="w-full">
      <AnimatePresence mode="wait">
        {!preview ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            {...getRootProps()}
            className={`
              relative border-2 border-dashed rounded-xl p-8 transition-all cursor-pointer
              ${
                isDragActive
                  ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                  : "border-gray-300 dark:border-dark-border hover:border-primary-400"
              }
            `}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center justify-center space-y-4">
              <motion.div
                animate={{ y: isDragActive ? -10 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <Upload className="w-12 h-12 text-gray-400" />
              </motion.div>
              <div className="text-center">
                <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
                  {isDragActive
                    ? "Drop your image here"
                    : "Drag & drop your image here"}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  or click to browse
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                  Supports JPEG, PNG, WebP up to {maxSize / 1024 / 1024}MB
                </p>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="preview"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="relative rounded-xl overflow-hidden bg-gray-100 dark:bg-dark-surface"
          >
            <img
              src={preview}
              alt="Preview"
              className="w-full h-auto max-h-96 object-contain"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 hover:opacity-100 transition-opacity">
              <button
                onClick={removeImage}
                className="absolute top-4 right-4 p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="absolute bottom-4 left-4 flex items-center space-x-2 text-white">
              <ImageIcon className="w-5 h-5" />
              <span className="text-sm font-medium">{file?.name}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
