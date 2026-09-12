import Link from "next/link";
import { ArrowRight, Search } from "lucide-react";
import PropertyCard from "@/components/PropertyCard";
import type { Property, PropertyResponse } from "@/lib/types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function getProperties(): Promise<Property[]> {
  try {
    const response = await fetch(`${API_URL}/api/v1/properties`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return [];
    }

    const data: PropertyResponse = await response.json();

    if (Array.isArray(data)) {
      return data;
    }

    return data.items;
  } catch {
    return [];
  }
}

export default async function HomePage() {
  const properties = await getProperties();

  return (
    <main className="min-h-screen bg-[#f7f5ef]">
      {/* Hero */}
      <section className="mx-auto max-w-7xl px-6 pb-16 pt-12 lg:px-8 lg:pt-20">
        <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <p className="mb-5 text-sm font-bold uppercase tracking-[0.2em] text-[#68736d]">
              Find your next place
            </p>

            <h1 className="max-w-3xl font-serif text-5xl leading-[1.05] tracking-tight text-[#173d2c] sm:text-6xl lg:text-7xl">
              Discover a property that feels like home.
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-8 text-[#68736d]">
              Explore verified properties and find the right home, apartment,
              or investment opportunity with the help of AI-powered search.
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                href="/properties"
                className="inline-flex items-center gap-2 rounded-full bg-[#173d2c] px-6 py-3.5 font-semibold text-white transition hover:bg-[#24563f]"
              >
                Explore properties
                <ArrowRight size={18} />
              </Link>

              <Link
                href="/ai-search"
                className="inline-flex items-center gap-2 rounded-full border border-[#173d2c]/15 bg-white px-6 py-3.5 font-semibold text-[#173d2c] transition hover:bg-[#eef2e8]"
              >
                <Search size={18} />
                AI Search
              </Link>
            </div>
          </div>

          <div className="relative overflow-hidden rounded-[32px]">
            <img
              src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1400&q=85"
              alt="Modern luxury house"
              className="aspect-[4/3] w-full object-cover"
            />
          </div>
        </div>
      </section>

      {/* Properties */}
      <section className="mx-auto max-w-7xl px-6 pb-20 lg:px-8">
        <div className="mb-8 flex items-end justify-between gap-4">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.15em] text-[#68736d]">
              Featured listings
            </p>

            <h2 className="mt-2 font-serif text-4xl text-[#173d2c]">
              Find your perfect property
            </h2>
          </div>

          <Link
            href="/properties"
            className="hidden items-center gap-2 font-semibold text-[#173d2c] sm:flex"
          >
            View all
            <ArrowRight size={17} />
          </Link>
        </div>

        {properties.length > 0 ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {properties.slice(0, 6).map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        ) : (
          <div className="rounded-[28px] border border-[#e8e5dc] bg-[#fffdf8] px-6 py-16 text-center">
            <h3 className="font-serif text-2xl text-[#173d2c]">
              No properties available yet
            </h3>

            <p className="mx-auto mt-2 max-w-md text-[#68736d]">
              Properties will appear here once they are added to the database.
            </p>

            <Link
              href="/properties"
              className="mt-6 inline-flex items-center gap-2 rounded-full bg-[#173d2c] px-5 py-3 font-semibold text-white"
            >
              Browse properties
              <ArrowRight size={17} />
            </Link>
          </div>
        )}
      </section>
    </main>
  );
}