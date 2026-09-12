
"use client";

import { useState } from "react";
import { Search, Sparkles, AlertCircle } from "lucide-react";

import { ragSearch } from "@/lib/api";
import type { Property } from "@/lib/types";
import PropertyCard from "@/components/PropertyCard";

export default function AISearchPage() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch() {
    if (!query.trim() || loading) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setProperties([]);

    try {
      const response = await ragSearch(query.trim());

      console.log("AI Search Response:", response);

      setAnswer(
        response.total > 0
          ? `Found ${response.total} matching properties based on your requirements.`
          : "No matching properties found."
      );

      const matchedProperties = response.items.map(
        (item) => item.property
      );

      setProperties(matchedProperties);

    } catch (err) {
      console.error("AI Search Error:", err);

      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong while connecting to the AI service.");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      handleSearch();
    }
  }

  function useExample(example: string) {
    setQuery(example);
  }

  return (
    <main className="min-h-screen bg-[#f7f5ef] px-5 py-16">
      <div className="mx-auto max-w-6xl">

        {/* Hero */}
        <section className="mx-auto max-w-4xl text-center">
          <div className="mx-auto mb-6 grid h-16 w-16 place-items-center rounded-2xl bg-[#173d2c] text-[#d9ef73] shadow-lg">
            <Sparkles size={28} />
          </div>

          <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#648b46]">
            EstateAI
          </p>

          <h1 className="mt-4 font-serif text-5xl leading-tight text-[#173d2c] md:text-6xl">
            Tell us what you&apos;re looking for.
          </h1>

          <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-[#68736d]">
            Describe your ideal property in your own words and let AI find
            properties that match your requirements.
          </p>

          {/* Search Box */}
          <div className="mt-10 rounded-3xl border border-[#e5e1d7] bg-white p-3 shadow-xl">
            <div className="flex flex-col gap-3 md:flex-row md:items-center">
              <div className="flex flex-1 items-center gap-3 px-4">
                <Search
                  size={22}
                  className="shrink-0 text-[#68736d]"
                />

                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={loading}
                  placeholder="e.g. 2 BHK apartment in Mumbai under ₹2 crore"
                  className="w-full bg-transparent py-4 text-base text-[#173d2c] outline-none placeholder:text-[#9aa19c]"
                />
              </div>

              <button
                onClick={handleSearch}
                disabled={loading || !query.trim()}
                className="rounded-2xl bg-[#173d2c] px-7 py-4 font-bold text-white transition hover:bg-[#24543e] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Searching..." : "Ask EstateAI"}
              </button>
            </div>
          </div>

          {/* Example Queries */}
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            <button
              onClick={() =>
                useExample("2 BHK apartment in Mumbai under ₹2 crore")
              }
              className="rounded-full border border-[#dedbd1] bg-white px-4 py-2 text-sm text-[#68736d] transition hover:border-[#173d2c] hover:text-[#173d2c]"
            >
              2 BHK under ₹2 Cr
            </button>

            <button
              onClick={() =>
                useExample("3 BHK apartment in Worli for rent")
              }
              className="rounded-full border border-[#dedbd1] bg-white px-4 py-2 text-sm text-[#68736d] transition hover:border-[#173d2c] hover:text-[#173d2c]"
            >
              3 BHK in Worli
            </button>

            <button
              onClick={() =>
                useExample("4 BHK luxury property in Mumbai")
              }
              className="rounded-full border border-[#dedbd1] bg-white px-4 py-2 text-sm text-[#68736d] transition hover:border-[#173d2c] hover:text-[#173d2c]"
            >
              Luxury 4 BHK
            </button>
          </div>
        </section>

        {/* Error */}
        {error && (
          <section className="mx-auto mt-10 max-w-4xl rounded-2xl border border-red-200 bg-red-50 p-5">
            <div className="flex items-start gap-3">
              <AlertCircle
                size={20}
                className="mt-0.5 shrink-0 text-red-600"
              />

              <div>
                <p className="font-bold text-red-800">
                  AI Search failed
                </p>

                <p className="mt-1 text-sm text-red-700">
                  {error}
                </p>

                <p className="mt-3 text-xs text-red-600">
                  Check that your FastAPI backend is running on
                  http://localhost:8000.
                </p>
              </div>
            </div>
          </section>
        )}

        {/* AI Response */}
        {answer && !error && (
          <section className="mx-auto mt-12 max-w-4xl">
            <div className="rounded-3xl border border-[#e5e1d7] bg-white p-7 shadow-sm md:p-9">
              <div className="flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-[#173d2c] text-[#d9ef73]">
                  <Sparkles size={18} />
                </div>

                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#648b46]">
                    EstateAI
                  </p>

                  <h2 className="font-serif text-2xl text-[#173d2c]">
                    AI response
                  </h2>
                </div>
              </div>

              <div className="mt-6 border-t border-[#eeeae1] pt-6">
                <p className="whitespace-pre-wrap leading-8 text-[#4e5953]">
                  {answer}
                </p>
              </div>
            </div>
          </section>
        )}

        {/* Recommended Properties */}
        {properties.length > 0 && (
          <section className="mt-16">
            <div className="mb-7 flex items-end justify-between gap-4">
              <div>
                <p className="text-sm font-bold uppercase tracking-[0.15em] text-[#648b46]">
                  AI recommendations
                </p>

                <h2 className="mt-2 font-serif text-4xl text-[#173d2c]">
                  Properties for you
                </h2>
              </div>

              <p className="hidden text-sm text-[#68736d] sm:block">
                {properties.length} matching properties
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {properties.map((property) => (
                <PropertyCard
                  key={property.id}
                  property={property}
                />
              ))}
            </div>
          </section>
        )}

        {/* No properties */}
        {answer && !error && properties.length === 0 && (
          <section className="mx-auto mt-10 max-w-4xl rounded-3xl border border-[#e5e1d7] bg-white p-8 text-center">
            <h3 className="font-serif text-2xl text-[#173d2c]">
              No matching properties found
            </h3>

            <p className="mt-2 text-[#68736d]">
              Try changing the location, budget, property type, or number
              of bedrooms.
            </p>
          </section>
        )}
      </div>
    </main>
  );
}
