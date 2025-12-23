/**
 * Slider Component - Range input for ratings
 * Used for 5-dimension player evaluation (1-5 scale)
 */
import * as React from "react";
import { cn } from "../../lib/utils";

interface SliderProps {
  /** Current value (1-5) */
  value: number;
  /** Callback when value changes */
  onChange: (value: number) => void;
  /** Minimum value (default: 1) */
  min?: number;
  /** Maximum value (default: 5) */
  max?: number;
  /** Step increment (default: 0.5) */
  step?: number;
  /** Label for the slider */
  label?: string;
  /** Disabled state */
  disabled?: boolean;
  /** Additional className */
  className?: string;
  /** Show value indicator */
  showValue?: boolean;
}

/**
 * Slider component for 1-5 ratings with visual feedback
 *
 * @example
 * <Slider
 *   label="Potencial"
 *   value={4.5}
 *   onChange={(val) => setValue(val)}
 *   showValue
 * />
 */
export default function Slider({
  value,
  onChange,
  min = 1,
  max = 5,
  step = 0.5,
  label,
  disabled = false,
  className,
  showValue = true,
}: SliderProps) {
  const percentage = ((value - min) / (max - min)) * 100;

  // Color based on value
  const getColor = (val: number) => {
    if (val >= 4.5) return "bg-green-500";
    if (val >= 3.5) return "bg-blue-500";
    if (val >= 2.5) return "bg-yellow-500";
    return "bg-red-500";
  };

  const getTextColor = (val: number) => {
    if (val >= 4.5) return "text-green-600";
    if (val >= 3.5) return "text-blue-600";
    if (val >= 2.5) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className={cn("w-full", className)}>
      {/* Label and Value */}
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-2">
          {label && (
            <label className="text-sm font-medium text-gray-700">{label}</label>
          )}
          {showValue && (
            <span className={cn("text-sm font-bold", getTextColor(value))}>
              {value.toFixed(1)}
            </span>
          )}
        </div>
      )}

      {/* Slider Track */}
      <div className="relative h-2 bg-gray-200 rounded-full">
        {/* Progress Fill */}
        <div
          className={cn("absolute h-full rounded-full transition-all", getColor(value))}
          style={{ width: `${percentage}%` }}
        />

        {/* Slider Input (invisible but functional) */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />

        {/* Thumb Indicator */}
        <div
          className={cn(
            "absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full shadow-md transition-all",
            "border-2 border-white",
            getColor(value),
            disabled ? "cursor-not-allowed" : "cursor-pointer"
          )}
          style={{ left: `calc(${percentage}% - 8px)` }}
        />
      </div>

      {/* Scale Markers */}
      <div className="flex justify-between mt-1 px-1">
        {Array.from({ length: max - min + 1 }, (_, i) => i + min).map((num) => (
          <span key={num} className="text-xs text-gray-400">
            {num}
          </span>
        ))}
      </div>
    </div>
  );
}
