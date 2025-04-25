"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface Suggestion {
    title: string;
    category: string;
    displayCategory: string;
}

export default function SearchAutoSuggest() {
    const inputRef = useRef<HTMLInputElement>(null);
    const listRef = useRef<HTMLUListElement>(null);

    const staticData: Suggestion[] = [
        { title: "VH-1001", category: "vehicles", displayCategory: "Vehicles" },
        { title: "BP-202", category: "battery_packs", displayCategory: "Battery Packs" },
        { title: "SIM-404", category: "sim_cards", displayCategory: "SIM Cards" },
        { title: "CHG-303", category: "chargers", displayCategory: "Chargers" },
        { title: "PT-ADV-001", category: "position_tracker_advanced", displayCategory: "Trackers" },
        { title: "VH-1041", category: "vehicles", displayCategory: "Vehicles" },
        { title: "BP-203", category: "battery_packs", displayCategory: "Battery Packs" },
        { title: "SIM-40444", category: "sim_cards", displayCategory: "SIM Cards" },
        { title: "CHG-3088", category: "chargers", displayCategory: "Chargers" },
        { title: "PT-ADV01", category: "position_tracker_advanced", displayCategory: "Trackers" },


    ];

    const [query, setQuery] = useState("");
    const [debouncedQuery, setDebouncedQuery] = useState("");
    const [isOpen, setIsOpen] = useState(false);
    const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);

    // Debounce the input
    useEffect(() => {
        const timeout = setTimeout(() => {
            setDebouncedQuery(query);
        }, 200);
        return () => clearTimeout(timeout);
    }, [query]);

    // Always show options, just filter if query is present
    const filteredOptions = useMemo(() => {
        if (!debouncedQuery) return staticData;
        return staticData.filter((item) =>
            item.title.toLowerCase().includes(debouncedQuery.toLowerCase())
        );
    }, [debouncedQuery]);

    const handleSelect = (option: Suggestion) => {
        console.log("Selected:", option);
        setQuery(option.title);
        setIsOpen(false);
        setHighlightedIndex(-1);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (!isOpen || filteredOptions.length === 0) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            setHighlightedIndex((prev) =>
                prev < filteredOptions.length - 1 ? prev + 1 : 0
            );
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setHighlightedIndex((prev) =>
                prev > 0 ? prev - 1 : filteredOptions.length - 1
            );
        } else if (e.key === "Enter" && highlightedIndex >= 0) {
            e.preventDefault();
            handleSelect(filteredOptions[highlightedIndex]);
        } else if (e.key === "Escape") {
            setIsOpen(false);
        }
    };

    return (
        <div className="relative w-[600px]">
            <Input
                ref={inputRef}
                placeholder="Search assets..."
                value={query}
                onChange={(e) => {
                    setQuery(e.target.value);
                    setIsOpen(true);
                }}
                onFocus={() => setIsOpen(true)}
                onKeyDown={handleKeyDown}
                onBlur={() => setTimeout(() => setIsOpen(false), 150)}
                className="bg-white text-black"
            />

            {isOpen && (
                <ul
                    ref={listRef}
                    className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md border border-gray-200 bg-white shadow-md"
                >
                    {filteredOptions.length === 0 ? (
                        <li className="px-4 py-2 text-sm text-muted-foreground">
                            No results found
                        </li>
                    ) : (
                        filteredOptions.map((option, index) => (
                            <li
                                key={option.title}
                                onClick={() => handleSelect(option)}
                                className={cn(
                                    "flex justify-between px-4 py-2 text-sm cursor-pointer",
                                    highlightedIndex === index
                                        ? "bg-blue-500 text-white"
                                        : "hover:bg-gray-100"
                                )}
                            >
                                <span>{option.title}</span>
                                <span className="italic text-gray-500">{option.displayCategory}</span>
                            </li>
                        ))
                    )}
                </ul>
            )}
        </div>
    );
}
