/**
 * Progress Component - Visual progress bar
 * Used for scraping status and async operations
 */
import { cn } from "../../lib/utils";

interface ProgressProps {
  /** Progress value (0-100) */
  value: number;
  /** Additional className */
  className?: string;
  /** Show percentage text */
  showValue?: boolean;
  /** Color variant */
  variant?: "default" | "success" | "warning" | "danger";
  /** Size variant */
  size?: "sm" | "md" | "lg";
}

/**
 * Progress bar component with percentage indicator
 *
 * @example
 * <Progress value={75} showValue variant="success" />
 */
export default function Progress({
  value,
  className,
  showValue = false,
  variant = "default",
  size = "md",
}: ProgressProps) {
  // Clamp value between 0-100
  const clampedValue = Math.min(Math.max(value, 0), 100);

  // Color variants
  const variantClasses = {
    default: "bg-blue-500",
    success: "bg-green-500",
    warning: "bg-yellow-500",
    danger: "bg-red-500",
  };

  // Size variants
  const sizeClasses = {
    sm: "h-1",
    md: "h-2",
    lg: "h-3",
  };

  return (
    <div className={cn("w-full", className)}>
      {showValue && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-700">Progresso</span>
          <span className="text-sm font-semibold text-gray-900">
            {clampedValue.toFixed(0)}%
          </span>
        </div>
      )}
      <div
        className={cn(
          "w-full bg-gray-200 rounded-full overflow-hidden",
          sizeClasses[size]
        )}
      >
        <div
          className={cn(
            "h-full transition-all duration-300 ease-in-out",
            variantClasses[variant]
          )}
          style={{ width: `${clampedValue}%` }}
        />
      </div>
    </div>
  );
}
