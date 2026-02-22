CREATE TABLE IF NOT EXISTS public.sellers(
    seller_id SERIAL PRIMARY KEY,
    is_verified_seller BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS public.ads(
    ad_id SERIAL PRIMARY KEY,
    seller_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category INTEGER NOT NULL,
    images_qty INTEGER NOT NULL,
    CONSTRAINT fk_ads_sellers
        FOREIGN KEY (seller_id)
        REFERENCES public.sellers(seller_id)
);