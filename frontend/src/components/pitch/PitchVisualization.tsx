/**
 * PitchVisualization Component - Football field with tactical positioning
 * Uses SVG for responsive field and Framer Motion for animations
 */
import { motion } from "framer-motion";
import { useShadowTeamStore, type Position } from "../../store/shadowTeamStore";
import type { JogadorWithDetails } from "../../types";

interface PitchVisualizationProps {
  /** Callback when position is clicked */
  onPositionClick?: (position: Position) => void;
  /** Show position labels */
  showLabels?: boolean;
  /** Interactive mode (allows clicking) */
  interactive?: boolean;
}

/**
 * Football pitch with tactical visualization
 * - Responsive SVG (viewBox adjusts automatically)
 * - Framer Motion transitions when formation changes
 * - Click positions to assign players
 *
 * @example
 * <PitchVisualization
 *   onPositionClick={(pos) => setSelectedPosition(pos)}
 *   interactive
 * />
 */
export default function PitchVisualization({
  onPositionClick,
  showLabels = true,
  interactive = true,
}: PitchVisualizationProps) {
  const { positions } = useShadowTeamStore();

  return (
    <div className="w-full bg-gradient-to-b from-green-600 to-green-700 rounded-lg shadow-lg p-4">
      <svg
        viewBox="0 0 100 140"
        className="w-full h-auto"
        style={{ maxHeight: "800px" }}
      >
        {/* Field Background */}
        <rect
          x="0"
          y="0"
          width="100"
          height="140"
          fill="#2D5016"
          stroke="#FFFFFF"
          strokeWidth="0.5"
        />

        {/* Horizontal Lines (Stripes) */}
        {Array.from({ length: 14 }).map((_, i) => (
          <rect
            key={`stripe-${i}`}
            x="0"
            y={i * 10}
            width="100"
            height="5"
            fill={i % 2 === 0 ? "#2D5016" : "#3A6B1E"}
            opacity="0.3"
          />
        ))}

        {/* Center Line */}
        <line
          x1="0"
          y1="70"
          x2="100"
          y2="70"
          stroke="#FFFFFF"
          strokeWidth="0.3"
        />

        {/* Center Circle */}
        <circle
          cx="50"
          cy="70"
          r="8"
          fill="none"
          stroke="#FFFFFF"
          strokeWidth="0.3"
        />
        <circle cx="50" cy="70" r="0.5" fill="#FFFFFF" />

        {/* Top Penalty Area */}
        <rect
          x="30"
          y="0"
          width="40"
          height="15"
          fill="none"
          stroke="#FFFFFF"
          strokeWidth="0.3"
        />
        <rect
          x="40"
          y="0"
          width="20"
          height="6"
          fill="none"
          stroke="#FFFFFF"
          strokeWidth="0.3"
        />
        <circle cx="50" cy="11" r="0.5" fill="#FFFFFF" />

        {/* Bottom Penalty Area */}
        <rect
          x="30"
          y="125"
          width="40"
          height="15"
          fill="none"
          stroke="#FFFFFF"
          strokeWidth="0.3"
        />
        <rect
          x="40"
          y="134"
          width="20"
          height="6"
          fill="none"
          stroke="#FFFFFF"
          strokeWidth="0.3"
        />
        <circle cx="50" cy="129" r="0.5" fill="#FFFFFF" />

        {/* Corner Arcs */}
        <circle cx="0" cy="0" r="2" fill="none" stroke="#FFFFFF" strokeWidth="0.3" />
        <circle cx="100" cy="0" r="2" fill="none" stroke="#FFFFFF" strokeWidth="0.3" />
        <circle cx="0" cy="140" r="2" fill="none" stroke="#FFFFFF" strokeWidth="0.3" />
        <circle cx="100" cy="140" r="2" fill="none" stroke="#FFFFFF" strokeWidth="0.3" />

        {/* Player Positions */}
        {positions.map((position) => (
          <PlayerMarker
            key={position.id}
            position={position}
            onClick={() => interactive && onPositionClick?.(position)}
            showLabel={showLabels}
            interactive={interactive}
          />
        ))}
      </svg>
    </div>
  );
}

/**
 * Player Marker Component - Animated position with player info
 */
function PlayerMarker({
  position,
  onClick,
  showLabel,
  interactive,
}: {
  position: Position;
  onClick: () => void;
  showLabel: boolean;
  interactive: boolean;
}) {
  const hasPlayer = !!position.player;

  return (
    <motion.g
      initial={{ x: position.x, y: position.y }}
      animate={{ x: position.x, y: position.y }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      onClick={onClick}
      className={interactive ? "cursor-pointer" : ""}
    >
      {/* Player Circle */}
      <motion.circle
        cx={0}
        cy={0}
        r={hasPlayer ? 4 : 3}
        fill={hasPlayer ? "#3B82F6" : "#FFFFFF"}
        stroke={hasPlayer ? "#FFFFFF" : "#3B82F6"}
        strokeWidth={hasPlayer ? 0.5 : 0.3}
        whileHover={interactive ? { scale: 1.2 } : {}}
        whileTap={interactive ? { scale: 0.9 } : {}}
      />

      {/* Player Number/Initial (if assigned) */}
      {hasPlayer && position.player && (
        <text
          x={0}
          y={1}
          textAnchor="middle"
          fontSize="3"
          fontWeight="bold"
          fill="#FFFFFF"
          pointerEvents="none"
        >
          {position.player.nome.charAt(0)}
        </text>
      )}

      {/* Position Label */}
      {showLabel && (
        <text
          x={0}
          y={hasPlayer ? 8 : 7}
          textAnchor="middle"
          fontSize="2.5"
          fontWeight="600"
          fill="#FFFFFF"
          pointerEvents="none"
          opacity="0.9"
        >
          {position.role}
        </text>
      )}

      {/* Player Name (if assigned) */}
      {hasPlayer && position.player && (
        <text
          x={0}
          y={11}
          textAnchor="middle"
          fontSize="2"
          fill="#FFFFFF"
          pointerEvents="none"
          opacity="0.8"
        >
          {position.player.nome.split(" ")[0]}
        </text>
      )}
    </motion.g>
  );
}
