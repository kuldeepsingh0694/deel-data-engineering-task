CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE staging.products (
     product_id       BIGSERIAL NOT NULL ,
    product_name     VARCHAR(500) NOT NULL,
    barcode          VARCHAR(26) NOT NULL,
    unity_price      DECIMAL NOT NULL,
    is_active        BOOLEAN,
    updated_at       TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    updated_by       BIGINT,
    created_at       TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    created_by       BIGINT,
    extract_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staging.customers (
    customer_id      BIGSERIAL NOT NULL ,
    customer_name    VARCHAR(500) NOT NULL,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    customer_address VARCHAR(500),
    updated_at       TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    updated_by       BIGINT,
    created_at       TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    created_by       BIGINT,
    extract_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staging.orders (
     order_id         BIGSERIAL NOT NULL ,
    order_date       DATE,
    delivery_date    DATE,
    customer_id      BIGINT,
    status           VARCHAR,
    updated_at       TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    updated_by       BIGINT,
    created_at       TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    created_by       BIGINT,
    extract_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staging.order_items (
   order_item_id    BIGSERIAL NOT NULL ,
    order_id         BIGINT,
    product_id       BIGINT,
    quanity          INTEGER,
    updated_at       TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    updated_by       BIGINT,
    created_at       TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    created_by       BIGINT,
    extract_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--