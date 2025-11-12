-- olist_schema.sql
CREATE DATABASE IF NOT EXISTS olist_db
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
USE olist_db;

-- customers
CREATE TABLE IF NOT EXISTS customers (
  customer_id VARCHAR(64) NOT NULL PRIMARY KEY,
  customer_unique_id VARCHAR(64) NOT NULL,
  customer_zip_code_prefix INT,
  customer_city VARCHAR(150),
  customer_state CHAR(2),
  INDEX (customer_unique_id),
  INDEX (customer_zip_code_prefix)
);

-- geolocation (note: same zip prefixes repeat — not unique)
CREATE TABLE IF NOT EXISTS geolocation (
  geolocation_zip_code_prefix INT,
  geolocation_lat DECIMAL(10,8),
  geolocation_lng DECIMAL(11,8),
  geolocation_city VARCHAR(150),
  geolocation_state CHAR(2),
  INDEX (geolocation_zip_code_prefix),
  INDEX (geolocation_state)
);

-- sellers
CREATE TABLE IF NOT EXISTS sellers (
  seller_id VARCHAR(64) NOT NULL PRIMARY KEY,
  seller_zip_code_prefix INT,
  seller_city VARCHAR(150),
  seller_state CHAR(2),
  INDEX (seller_zip_code_prefix),
  INDEX (seller_state)
);

-- products
CREATE TABLE IF NOT EXISTS products (
  product_id VARCHAR(64) NOT NULL PRIMARY KEY,
  product_category_name VARCHAR(150),
  product_name_length INT,
  product_description_length INT,
  product_photos_qty INT,
  product_weight_g INT,
  product_length_cm INT,
  product_height_cm INT,
  product_width_cm INT,
  INDEX (product_category_name)
);

-- category translation
CREATE TABLE IF NOT EXISTS category_translation (
  product_category_name VARCHAR(150) NOT NULL,
  product_category_name_english VARCHAR(150),
  PRIMARY KEY (product_category_name)
);

-- orders
CREATE TABLE IF NOT EXISTS orders (
  order_id VARCHAR(64) NOT NULL PRIMARY KEY,
  customer_id VARCHAR(64),
  order_status VARCHAR(50),
  order_purchase_timestamp DATETIME,
  order_approved_at DATETIME,
  order_delivered_carrier_date DATETIME,
  order_delivered_customer_date DATETIME,
  order_estimated_delivery_date DATETIME,
  CONSTRAINT fk_orders_customers FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  INDEX (customer_id),
  INDEX (order_purchase_timestamp)
);

-- order_items
CREATE TABLE IF NOT EXISTS order_items (
  order_id VARCHAR(64) NOT NULL,
  order_item_id INT NOT NULL,
  product_id VARCHAR(64),
  seller_id VARCHAR(64),
  shipping_limit_date DATETIME,
  price DECIMAL(10,2),
  freight_value DECIMAL(10,2),
  PRIMARY KEY (order_id, order_item_id),
  CONSTRAINT fk_items_order FOREIGN KEY (order_id)
    REFERENCES orders(order_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_items_product FOREIGN KEY (product_id)
    REFERENCES products(product_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT fk_items_seller FOREIGN KEY (seller_id)
    REFERENCES sellers(seller_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  INDEX (product_id),
  INDEX (seller_id)
);

-- order_payments
CREATE TABLE IF NOT EXISTS order_payments (
  order_id VARCHAR(64),
  payment_sequential INT,
  payment_type VARCHAR(50),
  payment_installments INT,
  payment_value DECIMAL(10,2),
  PRIMARY KEY (order_id, payment_sequential),
  CONSTRAINT fk_payments_order FOREIGN KEY (order_id)
    REFERENCES orders(order_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  INDEX (payment_type)
);

-- order_reviews
CREATE TABLE IF NOT EXISTS order_reviews (
  review_id VARCHAR(64) NOT NULL PRIMARY KEY,
  order_id VARCHAR(64),
  review_score TINYINT,
  review_comment_title TEXT,
  review_comment_message TEXT,
  review_creation_date DATETIME,
  review_answer_timestamp DATETIME,
  CONSTRAINT fk_reviews_order FOREIGN KEY (order_id)
    REFERENCES orders(order_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  INDEX (review_score),
  INDEX (review_creation_date)
);
