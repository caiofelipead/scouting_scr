/**
 * Dashboard Store - Zustand
 * Manages global dashboard filters and preferences
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface DashboardFilters {
  ageRange: [number, number];
  selectedPositions: string[];
  minMedia: number;
  maxValorMercado: number | null;
}

interface DashboardState {
  filters: DashboardFilters;
  setAgeRange: (range: [number, number]) => void;
  setSelectedPositions: (positions: string[]) => void;
  setMinMedia: (media: number) => void;
  setMaxValorMercado: (valor: number | null) => void;
  resetFilters: () => void;
}

const DEFAULT_FILTERS: DashboardFilters = {
  ageRange: [16, 35],
  selectedPositions: [],
  minMedia: 0,
  maxValorMercado: null,
};

/**
 * Dashboard Store - Persists filter preferences
 */
export const useDashboardStore = create<DashboardState>()(
  persist(
    (set) => ({
      filters: DEFAULT_FILTERS,

      setAgeRange: (range) => {
        set((state) => ({
          filters: { ...state.filters, ageRange: range },
        }));
      },

      setSelectedPositions: (positions) => {
        set((state) => ({
          filters: { ...state.filters, selectedPositions: positions },
        }));
      },

      setMinMedia: (media) => {
        set((state) => ({
          filters: { ...state.filters, minMedia: media },
        }));
      },

      setMaxValorMercado: (valor) => {
        set((state) => ({
          filters: { ...state.filters, maxValorMercado: valor },
        }));
      },

      resetFilters: () => {
        set({ filters: DEFAULT_FILTERS });
      },
    }),
    {
      name: "dashboard-filters-storage",
    }
  )
);
