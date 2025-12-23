/**
 * Shadow Team Store - Zustand
 * Manages tactical formation and player positioning
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { JogadorWithDetails } from "../types";

export type Formation = "4-3-3" | "4-4-2" | "3-5-2";

export interface Position {
  id: string;
  x: number; // Percentage of field width (0-100)
  y: number; // Percentage of field height (0-100)
  role: string;
  player: JogadorWithDetails | null;
}

interface ShadowTeamState {
  formation: Formation;
  positions: Position[];
  setFormation: (formation: Formation) => void;
  assignPlayer: (positionId: string, player: JogadorWithDetails | null) => void;
  clearAllPlayers: () => void;
  loadFormation: (formation: Formation) => void;
}

/**
 * Formation templates - Position coordinates on field
 */
const FORMATIONS: Record<Formation, Omit<Position, "player">[]> = {
  "4-3-3": [
    // Goalkeeper
    { id: "gk", x: 50, y: 95, role: "GOL" },
    // Defenders
    { id: "lb", x: 20, y: 75, role: "LE" },
    { id: "cb1", x: 40, y: 80, role: "ZAG" },
    { id: "cb2", x: 60, y: 80, role: "ZAG" },
    { id: "rb", x: 80, y: 75, role: "LD" },
    // Midfielders
    { id: "cdm", x: 50, y: 60, role: "VOL" },
    { id: "cm1", x: 35, y: 50, role: "MC" },
    { id: "cm2", x: 65, y: 50, role: "MC" },
    // Forwards
    { id: "lw", x: 20, y: 25, role: "AE" },
    { id: "st", x: 50, y: 15, role: "ATA" },
    { id: "rw", x: 80, y: 25, role: "AD" },
  ],
  "4-4-2": [
    // Goalkeeper
    { id: "gk", x: 50, y: 95, role: "GOL" },
    // Defenders
    { id: "lb", x: 20, y: 75, role: "LE" },
    { id: "cb1", x: 40, y: 80, role: "ZAG" },
    { id: "cb2", x: 60, y: 80, role: "ZAG" },
    { id: "rb", x: 80, y: 75, role: "LD" },
    // Midfielders
    { id: "lm", x: 20, y: 50, role: "ME" },
    { id: "cm1", x: 40, y: 55, role: "MC" },
    { id: "cm2", x: 60, y: 55, role: "MC" },
    { id: "rm", x: 80, y: 50, role: "MD" },
    // Forwards
    { id: "st1", x: 40, y: 20, role: "ATA" },
    { id: "st2", x: 60, y: 20, role: "ATA" },
  ],
  "3-5-2": [
    // Goalkeeper
    { id: "gk", x: 50, y: 95, role: "GOL" },
    // Defenders
    { id: "cb1", x: 30, y: 80, role: "ZAG" },
    { id: "cb2", x: 50, y: 82, role: "ZAG" },
    { id: "cb3", x: 70, y: 80, role: "ZAG" },
    // Midfielders
    { id: "lwb", x: 15, y: 60, role: "ALE" },
    { id: "cm1", x: 35, y: 55, role: "MC" },
    { id: "cdm", x: 50, y: 65, role: "VOL" },
    { id: "cm2", x: 65, y: 55, role: "MC" },
    { id: "rwb", x: 85, y: 60, role: "ALD" },
    // Forwards
    { id: "st1", x: 40, y: 20, role: "ATA" },
    { id: "st2", x: 60, y: 20, role: "ATA" },
  ],
};

/**
 * Shadow Team Store - Persists formation and player assignments
 */
export const useShadowTeamStore = create<ShadowTeamState>()(
  persist(
    (set) => ({
      formation: "4-3-3",
      positions: FORMATIONS["4-3-3"].map((pos) => ({ ...pos, player: null })),

      setFormation: (formation) => {
        set({
          formation,
          positions: FORMATIONS[formation].map((pos) => ({
            ...pos,
            player: null,
          })),
        });
      },

      assignPlayer: (positionId, player) => {
        set((state) => ({
          positions: state.positions.map((pos) =>
            pos.id === positionId ? { ...pos, player } : pos
          ),
        }));
      },

      clearAllPlayers: () => {
        set((state) => ({
          positions: state.positions.map((pos) => ({ ...pos, player: null })),
        }));
      },

      loadFormation: (formation) => {
        set({
          formation,
          positions: FORMATIONS[formation].map((pos) => ({ ...pos, player: null })),
        });
      },
    }),
    {
      name: "shadow-team-storage",
    }
  )
);
