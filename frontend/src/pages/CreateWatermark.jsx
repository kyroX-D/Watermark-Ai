// File: frontend/src/pages/CreateWatermark.jsx

import { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useDropzone } from "react-dropzone";
import { 
  Upload, Image as ImageIcon, Type, Move, Palette, Eye, 
  Wand2, Download, Loader, Sparkles, Grid3X3, Shield,
  AlertCircle, Check, ChevronDown
} from "lucide-react";
import toast from "react-hot-toast";

import DashboardLayout from "../components/dashboard/DashboardLayout";
import { watermarkService } from "../services/watermark";
import { validators } from "../utils/validators";
import { getImageDimensions } from "../utils/helpers";
import { useAuthStore } from "../hooks/useAuth";
import ModernSlider from "../components/common/ModernSlider";
import api from "../services/api";

// Enhanced Watermark Preview Component
const WatermarkPreview = ({ imageFile, watermarkText, settings }) => {
  const [imageUrl, setImageUrl] = useState(null);

  useEffect(() => {
    if (imageFile) {
      const url = URL.createObjectURL(imageFile);
      setImageUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [imageFile]);

  if (!imageUrl || !watermarkText) return null;

  const getPositionStyles = () => {
    const positions = {
      "top-left": { top: "10%", left: "10%" },
      "top-center": { top: "10%", left: "50%", transform: "translateX(-50%)" },
      "top-right": { top: "10%", right: "10%" },
      "left-center": { top: "50%", left: "10%", transform: "translateY(-50%)" },
      "center": { top: "50%", left: "50%", transform: "translate(-50%, -50%)" },
      "right-center": { top: "50%", right: "10%", transform: "translateY(-50%)" },
      "bottom-left": { bottom: "10%", left: "10%" },
      "bottom-center": { bottom: "10%", left: "50%", transform: "translateX(-50%)" },
      "bottom-right": { bottom: "10%", right: "10%" },
      "auto": { top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
    };
    return positions[settings.position] || positions["bottom-right"];
  };

  const getFontSize = () => {
    const sizes = { small: "14px", medium: "20px", large: "28px" };
    return sizes[settings.size] || "20px";
  };

  const renderMultipleWatermarks = () => {
    if (!settings.multipleWatermarks) return null;

    const positions = [];
    
    if (settings.pattern === "diagonal") {
      for (let i = 0; i < 5; i++) {
        const progress = i / 4;
        positions.push({
          left: `${progress * 80 + 10}%`,
          top: `${(1 - progress) * 80 + 10}%`
        });
      }
    } else if (settings.pattern === "grid") {
      for (let row = 0; row < 3; row++) {
        for (let col = 0; col < 3; col++) {
          positions.push({
            left: `${col * 30 + 20}%`,
            top: `${row * 30 + 20}%`
          });
        }
      }
    }

    return positions.map((pos, index) => (
      <div
        key={index}
        className="absolute font-semibold"
        style={{
          ...pos,
          fontSize: getFontSize(),
          opacity: settings.opacity,
          color: settings.textColor,
          textShadow: settings.textShadow ? "2px 2px 4px rgba(0,0,0,0.5)" : "none"
        }}
      >
        {watermarkText}
      </div>
    ));
  };

  return (
    <div className="relative overflow-hidden rounded-lg">
      <img src={imageUrl} alt="Preview" className="w-full h-auto" />
      
      {settings.multipleWatermarks ? (
        renderMultipleWatermarks()
      ) : (
        <div
          className="absolute font-semibold transition-all duration-300"
          style={{
            ...getPositionStyles(),
            fontSize: getFontSize(),
            opacity: settings.opacity,
            color: settings.textColor,
            textShadow: settings.textShadow ? "2px 2px 4px rgba(0,0,0,0.5)" : "none",
            fontFamily: settings.fontFamily || "Arial"
          }}
        >
          {watermarkText}
        </div>
      )}
      
      {settings.position === "auto" && (
        <div className="absolute top-2 left-2 bg-primary-600 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1">
          <Sparkles className="w-3 h-3" />
          AI Position
        </div>
      )}
    </div>
  );
};

function CreateWatermark() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [watermarkText, setWatermarkText] = useState("");
  const [imageDimensions, setImageDimensions] = useState(null);
  const [availableFonts, setAvailableFonts] = useState([]);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  
  // Enhanced watermark settings
  const [watermarkSettings, setWatermarkSettings] = useState({
    position: "bottom-right",
    size: "medium",
    opacity: 0.7,
    autoOpacity: false,
    multipleWatermarks: false,
    pattern: "diagonal",
    fontFamily: "Arial",
    textColor: "#FFFFFF",
    textShadow: false,
    protectionMode: "standard"
  });

  // Load available fonts
  useEffect(() => {
    loadAvailableFonts();
  }, []);

  const loadAvailableFonts = async () => {
    try {
      const response = await api.get("/watermarks/fonts");
      setAvailableFonts(response.data);
    } catch (error) {
      console.error("Failed to load fonts:", error);
    }
  };

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const error = validators.imageFile(file);
      if (error) {
        toast.error(error);
        return;
      }

      setSelectedFile(file);
      try {
        const dimensions = await getImageDimensions(file);
        setImageDimensions(dimensions);
      } catch (err) {
        console.error("Failed to get image dimensions:", err);
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".webp"],
    },
    maxFiles: 1,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    const textError = validators.watermarkText(watermarkText);
    if (textError) {
      toast.error(textError);
      return;
    }

    if (!selectedFile) {
      toast.error("Please select an image");
      return;
    }

    setIsProcessing(true);
    try {
      const result = await watermarkService.create(
        selectedFile, 
        watermarkText,
        watermarkSettings
      );
      
      toast.success("Watermark created successfully!");
      navigate("/my-images");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create watermark");
    } finally {
      setIsProcessing(false);
    }
  };

  const isProUser = user?.subscription_tier === "pro" || user?.subscription_tier === "elite";
  const isEliteUser = user?.subscription_tier === "elite";

  const positions = [
    { value: "top-left", label: "Top Left", icon: "↖" },
    { value: "top-center", label: "Top Center", icon: "↑" },
    { value: "top-right", label: "Top Right", icon: "↗" },
    { value: "left-center", label: "Left Center", icon: "←" },
    { value: "center", label: "Center", icon: "•" },
    { value: "right-center", label: "Right Center", icon: "→" },
    { value: "bottom-left", label: "Bottom Left", icon: "↙" },
    { value: "bottom-center", label: "Bottom Center", icon: "↓" },
    { value: "bottom-right", label: "Bottom Right", icon: "↘" },
  ];

  if (isProUser) {
    positions.push({ 
      value: "auto", 
      label: "Auto (AI chooses)", 
      icon: <Sparkles className="w-4 h-4" />,
      premium: true 
    });
  }

  const protectionModes = [
    { 
      value: "standard", 
      label: "Standard", 
      description: "Basic watermark protection",
      icon: <Shield className="w-4 h-4" />
    },
    { 
      value: "contextual", 
      label: "Contextual", 
      description: "Blends naturally with image",
      icon: <Wand2 className="w-4 h-4" />,
      premium: true,
      requiresAuto: true
    },
    { 
      value: "multilayer", 
      label: "Multi-Layer", 
      description: "Enhanced AI-resistant protection",
      icon: <Grid3X3 className="w-4 h-4" />,
      premium: true
    }
  ];

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          <div>
            <h1 className="text-3xl font-bold mb-2">Create AI-Protected Watermark</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Upload an image and add your custom watermark with advanced AI protection
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Column - Upload & Settings */}
            <div className="space-y-6">
              {/* Upload Area */}
              <div className="card p-6">
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                    ${isDragActive
                      ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                      : "border-gray-300 dark:border-gray-600 hover:border-primary-400"
                    }`}
                >
                  <input {...getInputProps()} />
                  <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg font-medium mb-2">
                    {isDragActive
                      ? "Drop the image here"
                      : "Drag & drop an image here"}
                  </p>
                  <p className="text-sm text-gray-500">
                    or click to select (Max 10MB)
                  </p>
                </div>

                {selectedFile && (
                  <div className="mt-4 p-4 bg-gray-50 dark:bg-dark-bg rounded-lg">
                    <div className="flex items-center space-x-3">
                      <ImageIcon className="w-8 h-8 text-primary-500" />
                      <div className="flex-1">
                        <p className="font-medium">{selectedFile.name}</p>
                        <p className="text-sm text-gray-500">
                          {imageDimensions &&
                            `${imageDimensions.width} × ${imageDimensions.height}px`}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Watermark Settings */}
              <form onSubmit={handleSubmit} className="card p-6 space-y-6">
                {/* Watermark Text */}
                <div>
                  <label className="flex items-center text-sm font-medium mb-2">
                    <Type className="w-4 h-4 mr-2" />
                    Watermark Text
                  </label>
                  <input
                    type="text"
                    value={watermarkText}
                    onChange={(e) => setWatermarkText(e.target.value)}
                    placeholder="Enter your watermark text"
                    className="input-field"
                    maxLength={100}
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {watermarkText.length}/100 characters
                  </p>
                </div>

                {/* Position Grid */}
                <div>
                  <label className="flex items-center text-sm font-medium mb-2">
                    <Move className="w-4 h-4 mr-2" />
                    Position
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {positions.map((pos) => (
                      <button
                        key={pos.value}
                        type="button"
                        onClick={() => setWatermarkSettings({...watermarkSettings, position: pos.value})}
                        disabled={pos.premium && !isProUser}
                        className={`
                          relative p-3 rounded-lg border-2 transition-all
                          ${watermarkSettings.position === pos.value
                            ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                            : "border-gray-200 dark:border-gray-700 hover:border-gray-300"
                          }
                          ${pos.premium && !isProUser ? "opacity-50 cursor-not-allowed" : ""}
                        `}
                      >
                        <div className="flex flex-col items-center gap-1">
                          <span className="text-lg">{pos.icon}</span>
                          <span className="text-xs">{pos.label}</span>
                        </div>
                        {pos.premium && !isProUser && (
                          <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs px-1 rounded">
                            PRO
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Size */}
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Text Size
                  </label>
                  <div className="flex space-x-4">
                    {["small", "medium", "large"].map((size) => (
                      <label key={size} className="flex items-center">
                        <input
                          type="radio"
                          name="size"
                          value={size}
                          checked={watermarkSettings.size === size}
                          onChange={(e) => setWatermarkSettings({...watermarkSettings, size: e.target.value})}
                          className="mr-2"
                        />
                        <span className="capitalize">{size}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Opacity with Modern Slider */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="flex items-center text-sm font-medium">
                      <Eye className="w-4 h-4 mr-2" />
                      Opacity: {Math.round(watermarkSettings.opacity * 100)}%
                    </label>
                    {isProUser && (
                      <label className="flex items-center text-sm">
                        <input
                          type="checkbox"
                          checked={watermarkSettings.autoOpacity}
                          onChange={(e) => setWatermarkSettings({
                            ...watermarkSettings, 
                            autoOpacity: e.target.checked
                          })}
                          className="mr-2"
                        />
                                                  <span className="flex items-center gap-1">
                            <Sparkles className="w-3 h-3" />
                            Auto Opacity
                          </span>
                        </span>
                      </label>
                    )}
                  </div>
                  <ModernSlider
                    value={watermarkSettings.opacity}
                    onChange={(value) => setWatermarkSettings({...watermarkSettings, opacity: value})}
                    min={0.1}
                    max={1}
                    step={0.1}
                    disabled={watermarkSettings.autoOpacity}
                  />
                </div>

                {/* Advanced Options Toggle */}
                <button
                  type="button"
                  onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                  className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-bg rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <span className="font-medium">Advanced Options</span>
                  <ChevronDown className={`w-5 h-5 transition-transform ${showAdvancedOptions ? "rotate-180" : ""}`} />
                </button>

                {/* Advanced Options */}
                <AnimatePresence>
                  {showAdvancedOptions && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="space-y-6 overflow-hidden"
                    >
                      {/* Multiple Watermarks */}
                      <div className="p-4 bg-gray-50 dark:bg-dark-bg rounded-lg">
                        <label className="flex items-center justify-between mb-4">
                          <span className="flex items-center font-medium">
                            <Grid3X3 className="w-4 h-4 mr-2" />
                            Multiple Watermarks
                          </span>
                          <input
                            type="checkbox"
                            checked={watermarkSettings.multipleWatermarks}
                            onChange={(e) => setWatermarkSettings({
                              ...watermarkSettings, 
                              multipleWatermarks: e.target.checked
                            })}
                            className="toggle"
                          />
                        </label>
                        
                        {watermarkSettings.multipleWatermarks && (
                          <div className="space-y-3">
                            <label className="text-sm font-medium">Pattern</label>
                            <div className="grid grid-cols-3 gap-2">
                              {["diagonal", "grid", "random"].map((pattern) => (
                                <button
                                  key={pattern}
                                  type="button"
                                  onClick={() => setWatermarkSettings({
                                    ...watermarkSettings, 
                                    pattern
                                  })}
                                  className={`
                                    p-2 rounded-lg border-2 capitalize transition-all
                                    ${watermarkSettings.pattern === pattern
                                      ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                                      : "border-gray-200 dark:border-gray-700"
                                    }
                                  `}
                                >
                                  {pattern}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Font Selection */}
                      <div>
                        <label className="text-sm font-medium mb-2 block">
                          Font Family
                        </label>
                        <select
                          value={watermarkSettings.fontFamily}
                          onChange={(e) => setWatermarkSettings({
                            ...watermarkSettings, 
                            fontFamily: e.target.value
                          })}
                          className="input-field"
                        >
                          {availableFonts.map((font) => (
                            <option 
                              key={font.name} 
                              value={font.name}
                              disabled={!font.available}
                            >
                              {font.name} {!font.available && `(${font.tier.toUpperCase()})`}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Text Color */}
                      {isProUser && (
                        <div>
                          <label className="flex items-center text-sm font-medium mb-2">
                            <Palette className="w-4 h-4 mr-2" />
                            Text Color
                          </label>
                          <div className="flex items-center gap-4">
                            <input
                              type="color"
                              value={watermarkSettings.textColor}
                              onChange={(e) => setWatermarkSettings({
                                ...watermarkSettings, 
                                textColor: e.target.value
                              })}
                              className="w-20 h-10 rounded cursor-pointer"
                            />
                            <input
                              type="text"
                              value={watermarkSettings.textColor}
                              onChange={(e) => setWatermarkSettings({
                                ...watermarkSettings, 
                                textColor: e.target.value
                              })}
                              className="input-field flex-1"
                              placeholder="#FFFFFF"
                            />
                          </div>
                        </div>
                      )}

                      {/* Text Shadow */}
                      {isEliteUser && (
                        <label className="flex items-center justify-between p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                          <span className="font-medium">Text Shadow</span>
                          <input
                            type="checkbox"
                            checked={watermarkSettings.textShadow}
                            onChange={(e) => setWatermarkSettings({
                              ...watermarkSettings, 
                              textShadow: e.target.checked
                            })}
                            className="toggle"
                          />
                        </label>
                      )}

                      {/* Protection Mode */}
                      <div>
                        <label className="text-sm font-medium mb-2 block">
                          Protection Mode
                        </label>
                        <div className="space-y-2">
                          {protectionModes.map((mode) => (
                            <button
                              key={mode.value}
                              type="button"
                              onClick={() => {
                                if (!mode.premium || isProUser) {
                                  setWatermarkSettings({
                                    ...watermarkSettings, 
                                    protectionMode: mode.value
                                  });
                                }
                              }}
                              disabled={
                                (mode.premium && !isProUser) || 
                                (mode.requiresAuto && watermarkSettings.position !== "auto")
                              }
                              className={`
                                w-full p-4 rounded-lg border-2 text-left transition-all
                                ${watermarkSettings.protectionMode === mode.value
                                  ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                                  : "border-gray-200 dark:border-gray-700 hover:border-gray-300"
                                }
                                ${(mode.premium && !isProUser) || (mode.requiresAuto && watermarkSettings.position !== "auto")
                                  ? "opacity-50 cursor-not-allowed" 
                                  : ""
                                }
                              `}
                            >
                              <div className="flex items-start gap-3">
                                <div className="mt-1">{mode.icon}</div>
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium">{mode.label}</span>
                                    {mode.premium && !isProUser && (
                                      <span className="bg-primary-600 text-white text-xs px-2 py-0.5 rounded">
                                        PRO
                                      </span>
                                    )}
                                  </div>
                                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    {mode.description}
                                  </p>
                                  {mode.requiresAuto && watermarkSettings.position !== "auto" && (
                                    <p className="text-xs text-amber-600 dark:text-amber-400 mt-1 flex items-center gap-1">
                                      <AlertCircle className="w-3 h-3" />
                                      Requires Auto position
                                    </p>
                                  )}
                                </div>
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                <button
                  type="submit"
                  disabled={isProcessing || !selectedFile || !watermarkText}
                  className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader className="w-5 h-5 animate-spin" />
                      Processing...
                    </span>
                  ) : (
                    "Create Watermark"
                  )}
                </button>
              </form>
            </div>

            {/* Right Column - Preview */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold mb-4">Preview</h2>
              {selectedFile && watermarkText ? (
                <WatermarkPreview
                  imageFile={selectedFile}
                  watermarkText={watermarkText}
                  settings={watermarkSettings}
                />
              ) : (
                <div className="aspect-video bg-gray-100 dark:bg-dark-bg rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">
                    Upload an image and enter text to see preview
                  </p>
                </div>
              )}
              
              {/* Settings Summary */}
              {selectedFile && watermarkText && (
                <div className="mt-4 p-4 bg-gray-50 dark:bg-dark-bg rounded-lg space-y-2 text-sm">
                  <h3 className="font-medium mb-2">Settings Summary</h3>
                  <div className="grid grid-cols-2 gap-2 text-gray-600 dark:text-gray-400">
                    <span>Position:</span>
                    <span className="capitalize">
                      {watermarkSettings.position === "auto" ? "AI Auto-Position" : watermarkSettings.position.replace("-", " ")}
                    </span>
                    <span>Size:</span>
                    <span className="capitalize">{watermarkSettings.size}</span>
                    <span>Opacity:</span>
                    <span>
                      {watermarkSettings.autoOpacity ? "AI Auto" : `${Math.round(watermarkSettings.opacity * 100)}%`}
                    </span>
                    <span>Protection:</span>
                    <span className="capitalize">{watermarkSettings.protectionMode}</span>
                    {watermarkSettings.multipleWatermarks && (
                      <>
                        <span>Pattern:</span>
                        <span className="capitalize">{watermarkSettings.pattern}</span>
                      </>
                    )}
                  </div>
                  
                  {/* AI Features Active */}
                  {(watermarkSettings.position === "auto" || watermarkSettings.autoOpacity || watermarkSettings.protectionMode !== "standard") && (
                    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                      <p className="text-xs font-medium text-primary-600 dark:text-primary-400 flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        AI Protection Active
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
}

export default CreateWatermark;