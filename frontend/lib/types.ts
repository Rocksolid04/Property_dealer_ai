export type PropertyImage = {
  id: number;
  image_url: string;
  storage_path: string;
  display_order: number;
};

export type Property = {
  id: number;
  title: string;
  description?: string | null;
  property_type: string;
  listing_type: string;
  location: string;
  price: number;
  bedrooms?: number | null;
  bathrooms?: number | null;
  area_sqft?: number | null;
  owner_id?: number | null;
  images?: PropertyImage[];
};

export type PropertyResponse =
  | Property[]
  | {
      items: Property[];
      total: number;
    };


export type AISearchItem = {
  property: Property;
  rrf_score: number;
};

export type AISearchResponse = {
  items: AISearchItem[];
  filters?: {
    location?: string | null;
    property_type?: string | null;
    listing_type?: string | null;
    min_price?: number | null;
    max_price?: number | null;
    bedrooms?: number | null;
    search_text?: string | null;
  };
  total: number;
  page: number;
  limit: number;
  total_pages: number;
};