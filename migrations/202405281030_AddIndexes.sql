-- migrate:up

create index hotel_rating_idx on hotel.hotels using btree(rating);

create extension pg_trgm;
create index hotel_name_trgm_idx on hotel.hotels using gist(name gist_trgm_ops);

-- migrate:down