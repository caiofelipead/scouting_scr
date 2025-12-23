/**
 * Combobox Component - Searchable select for players
 * Used in Comparador and Analytics pages
 */
import { useState, useEffect } from "react";
import { Check, ChevronsUpDown, X } from "lucide-react";
import { cn } from "../../lib/utils";
import { Button } from "./Button";

export interface ComboboxOption {
  value: string | number;
  label: string;
  metadata?: any;
}

interface ComboboxProps {
  /** Options to display */
  options: ComboboxOption[];
  /** Currently selected value */
  value?: string | number;
  /** Callback when selection changes */
  onChange: (value: string | number | null) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Empty state text */
  emptyText?: string;
  /** Allow clearing selection */
  clearable?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Additional className */
  className?: string;
}

/**
 * Combobox with search functionality
 *
 * @example
 * <Combobox
 *   options={jogadores.map(j => ({ value: j.id, label: j.nome }))}
 *   value={selectedId}
 *   onChange={(id) => setSelectedId(id)}
 *   placeholder="Selecione um jogador..."
 *   clearable
 * />
 */
export default function Combobox({
  options,
  value,
  onChange,
  placeholder = "Selecione...",
  emptyText = "Nenhum resultado encontrado",
  clearable = false,
  disabled = false,
  className,
}: ComboboxProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");

  // Filter options based on search
  const filteredOptions = options.filter((option) =>
    option.label.toLowerCase().includes(search.toLowerCase())
  );

  // Get selected option
  const selectedOption = options.find((option) => option.value === value);

  // Reset search when closing
  useEffect(() => {
    if (!open) {
      setSearch("");
    }
  }, [open]);

  const handleSelect = (selectedValue: string | number) => {
    onChange(selectedValue === value ? null : selectedValue);
    setOpen(false);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(null);
  };

  return (
    <div className={cn("relative", className)}>
      {/* Trigger Button */}
      <Button
        type="button"
        variant="outline"
        onClick={() => !disabled && setOpen(!open)}
        disabled={disabled}
        className="w-full justify-between"
      >
        <span className={cn(!selectedOption && "text-gray-400")}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <div className="flex items-center gap-1">
          {clearable && selectedOption && !disabled && (
            <X
              className="h-4 w-4 text-gray-400 hover:text-gray-600"
              onClick={handleClear}
            />
          )}
          <ChevronsUpDown className="h-4 w-4 opacity-50" />
        </div>
      </Button>

      {/* Dropdown */}
      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />

          {/* Options List */}
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-80 overflow-auto">
            {/* Search Input */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-2">
              <input
                type="text"
                placeholder="Buscar..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
            </div>

            {/* Options */}
            <div className="p-1">
              {filteredOptions.length === 0 ? (
                <div className="px-3 py-8 text-center text-sm text-gray-500">
                  {emptyText}
                </div>
              ) : (
                filteredOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSelect(option.value)}
                    className={cn(
                      "w-full flex items-center justify-between px-3 py-2 text-sm rounded-md transition-colors",
                      option.value === value
                        ? "bg-blue-50 text-blue-600 font-medium"
                        : "text-gray-700 hover:bg-gray-50"
                    )}
                  >
                    <span>{option.label}</span>
                    {option.value === value && (
                      <Check className="h-4 w-4" />
                    )}
                  </button>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
