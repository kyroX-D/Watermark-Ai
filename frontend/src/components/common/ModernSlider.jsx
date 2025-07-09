// File: frontend/src/components/common/ModernSlider.jsx

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";

export default function ModernSlider({ 
  value = 0.5, 
  onChange, 
  min = 0, 
  max = 1, 
  step = 0.01,
  disabled = false,
  className = ""
}) {
  const [isDragging, setIsDragging] = useState(false);
  const sliderRef = useRef(null);
  const [localValue, setLocalValue] = useState(value);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleMouseDown = (e) => {
    if (disabled) return;
    setIsDragging(true);
    updateValue(e);
  };

  const handleMouseMove = (e) => {
    if (!isDragging || disabled) return;
    updateValue(e);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleTouchStart = (e) => {
    if (disabled) return;
    setIsDragging(true);
    updateValue(e.touches[0]);
  };

  const handleTouchMove = (e) => {
    if (!isDragging || disabled) return;
    updateValue(e.touches[0]);
  };

  const updateValue = (e) => {
    if (!sliderRef.current) return;

    const rect = sliderRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, x / rect.width));
    const newValue = min + (max - min) * percentage;
    
    // Round to step
    const rounded = Math.round(newValue / step) * step;
    setLocalValue(rounded);
    onChange(rounded);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.addEventListener("touchmove", handleTouchMove);
      document.addEventListener("touchend", handleMouseUp);

      return () => {
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
        document.removeEventListener("touchmove", handleTouchMove);
        document.removeEventListener("touchend", handleMouseUp);
      };
    }
  }, [isDragging]);

  const percentage = ((localValue - min) / (max - min)) * 100;

  return (
    <div className={`relative ${className}`}>
      <div
        ref={sliderRef}
        className={`
          relative w-full h-10 flex items-center cursor-pointer
          ${disabled ? "opacity-50 cursor-not-allowed" : ""}
        `}
        onMouseDown={handleMouseDown}
        onTouchStart={handleTouchStart}
      >
        {/* Track */}
        <div className="absolute w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          {/* Fill */}
          <motion.div
            className="absolute h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full"
            style={{ width: `${percentage}%` }}
            initial={false}
            animate={{ width: `${percentage}%` }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          />
          
          {/* Glow effect */}
          {!disabled && (
            <motion.div
              className="absolute h-full bg-primary-400/30 blur-md"
              style={{ width: `${percentage}%` }}
              initial={false}
              animate={{ 
                width: `${percentage}%`,
                opacity: isDragging ? 0.5 : 0.3 
              }}
            />
          )}
        </div>

        {/* Thumb */}
        <motion.div
          className={`
            absolute w-6 h-6 bg-white dark:bg-gray-200 rounded-full shadow-lg
            border-2 border-primary-500 transform -translate-x-1/2
            ${!disabled && "hover:scale-110 active:scale-95"}
            ${isDragging ? "scale-110" : ""}
          `}
          style={{ left: `${percentage}%` }}
          initial={false}
          animate={{ 
            left: `${percentage}%`,
            scale: isDragging ? 1.1 : 1
          }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        >
          {/* Inner dot */}
          <div className="absolute inset-0 m-auto w-2 h-2 bg-primary-500 rounded-full" />
        </motion.div>

        {/* Value tooltip */}
        <AnimatePresence>
          {isDragging && !disabled && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="absolute -top-10 transform -translate-x-1/2 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs px-2 py-1 rounded"
              style={{ left: `${percentage}%` }}
            >
              {Math.round(localValue * 100)}%
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-gray-100" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Tick marks */}
      <div className="absolute w-full flex justify-between px-3 -bottom-5 text-xs text-gray-500">
        <span>{Math.round(min * 100)}%</span>
        <span>{Math.round(max * 100)}%</span>
      </div>
    </div>
  );
}

// Import AnimatePresence if not already imported
import { AnimatePresence } from "framer-motion";