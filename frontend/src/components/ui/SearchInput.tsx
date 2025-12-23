/**
 * SearchInput Component - Input de busca com debounce
 * Otimizado para evitar requisições excessivas
 */
import { useState, useEffect } from "react";
import { Search, X } from "lucide-react";
import { cn } from "../../lib/utils";
import { Input } from "./Input";

interface SearchInputProps {
  /** Valor inicial da busca */
  value?: string;
  /** Callback quando a busca mudar (após debounce) */
  onSearch: (query: string) => void;
  /** Placeholder do input */
  placeholder?: string;
  /** Tempo de debounce em ms */
  debounceMs?: number;
  /** Classe CSS adicional */
  className?: string;
}

/**
 * SearchInput - Input de busca com debounce e clear button
 *
 * @example
 * <SearchInput
 *   placeholder="Buscar jogadores..."
 *   onSearch={(query) => setFilters({ ...filters, nome: query })}
 *   debounceMs={500}
 * />
 */
export default function SearchInput({
  value = "",
  onSearch,
  placeholder = "Buscar...",
  debounceMs = 500,
  className,
}: SearchInputProps) {
  const [localValue, setLocalValue] = useState(value);

  // Debounce effect
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(localValue);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [localValue, debounceMs, onSearch]);

  // Sincroniza com valor externo
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleClear = () => {
    setLocalValue("");
    onSearch("");
  };

  return (
    <div className={cn("relative", className)}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
      <Input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder={placeholder}
        className="pl-10 pr-10"
      />
      {localValue && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Limpar busca"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
