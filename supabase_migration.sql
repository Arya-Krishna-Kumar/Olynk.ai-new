-- OLynk AI MVP Database Schema
-- Run this in your Supabase SQL Editor

-- Enable Row Level Security (RLS)
ALTER TABLE IF EXISTS products ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS insights ENABLE ROW LEVEL SECURITY;

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    product_id VARCHAR(255),
    product_name VARCHAR(500),
    category VARCHAR(255),
    brand VARCHAR(255),
    price DECIMAL(10,2),
    cost DECIMAL(10,2),
    sku VARCHAR(255),
    stock_quantity INTEGER,
    weight_g DECIMAL(8,2),
    dimensions_cm VARCHAR(255),
    launch_date DATE,
    last_updated TIMESTAMP,
    tags TEXT,
    description TEXT,
    status VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(255),
    order_date TIMESTAMP,
    customer_id VARCHAR(255),
    customer_name VARCHAR(500),
    product_id VARCHAR(255),
    product_name VARCHAR(500),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    payment_method VARCHAR(255),
    shipping_address TEXT,
    order_status VARCHAR(100),
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    grand_total DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    id BIGSERIAL PRIMARY KEY,
    customer_id VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(500),
    phone VARCHAR(50),
    registration_date DATE,
    total_orders INTEGER,
    total_spent DECIMAL(12,2),
    average_order_value DECIMAL(10,2),
    last_order_date DATE,
    preferred_payment_method VARCHAR(255),
    shipping_address TEXT,
    customer_segment VARCHAR(255),
    marketing_opt_in BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id BIGSERIAL PRIMARY KEY,
    inventory_id VARCHAR(255),
    product_id VARCHAR(255),
    product_name VARCHAR(500),
    sku VARCHAR(255),
    location VARCHAR(255),
    warehouse VARCHAR(255),
    current_stock INTEGER,
    minimum_stock INTEGER,
    maximum_stock INTEGER,
    unit_cost DECIMAL(10,2),
    total_value DECIMAL(12,2),
    last_restocked DATE,
    next_restock_date DATE,
    stock_status VARCHAR(100),
    category VARCHAR(255),
    supplier VARCHAR(255),
    lead_time_days INTEGER,
    reorder_point INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id BIGSERIAL PRIMARY KEY,
    analysis_type VARCHAR(100),
    data_type VARCHAR(100),
    analysis_data JSONB,
    total_revenue DECIMAL(12,2),
    total_customers INTEGER,
    total_products INTEGER,
    low_stock_items INTEGER,
    analysis_date TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create insights table
CREATE TABLE IF NOT EXISTS insights (
    id BIGSERIAL PRIMARY KEY,
    insight_type VARCHAR(100),
    insight_text TEXT,
    insight_data JSONB,
    priority_level VARCHAR(50),
    actionable BOOLEAN DEFAULT TRUE,
    insight_date TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_product_id ON products(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_customers_customer_id ON customers(customer_id);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory(sku);
CREATE INDEX IF NOT EXISTS idx_analytics_analysis_date ON analytics(analysis_date);
CREATE INDEX IF NOT EXISTS idx_insights_insight_date ON insights(insight_date);

-- Create RLS policies (allow all operations for now - you can restrict later)
CREATE POLICY "Allow all operations on products" ON products FOR ALL USING (true);
CREATE POLICY "Allow all operations on orders" ON orders FOR ALL USING (true);
CREATE POLICY "Allow all operations on customers" ON customers FOR ALL USING (true);
CREATE POLICY "Allow all operations on inventory" ON inventory FOR ALL USING (true);
CREATE POLICY "Allow all operations on analytics" ON analytics FOR ALL USING (true);
CREATE POLICY "Allow all operations on insights" ON insights FOR ALL USING (true);

-- Insert sample data for testing (optional)
INSERT INTO products (product_id, product_name, category, brand, price, cost, sku, stock_quantity, status) 
VALUES 
('P001', 'Sample Product 1', 'Electronics', 'Sample Brand', 999.99, 500.00, 'SKU001', 50, 'Active'),
('P002', 'Sample Product 2', 'Clothing', 'Sample Brand', 299.99, 150.00, 'SKU002', 25, 'Active')
ON CONFLICT DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inventory_updated_at BEFORE UPDATE ON inventory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

