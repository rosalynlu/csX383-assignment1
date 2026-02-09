-- Seed Data for Grocery Ordering System

-- Insert items
INSERT INTO items (name, category, quantity) VALUES
    ('bread', 'bread', 100),
    ('milk', 'dairy', 50),
    ('eggs', 'dairy', 75),
    ('chicken', 'meat', 40),
    ('beef', 'meat', 30),
    ('apples', 'produce', 80),
    ('bananas', 'produce', 90),
    ('soda', 'party', 60),
    ('napkins', 'party', 120);

-- Insert pricing
INSERT INTO pricing (item_id, price) VALUES
    ((SELECT id FROM items WHERE name = 'bread'), 3.99),
    ((SELECT id FROM items WHERE name = 'milk'), 4.50),
    ((SELECT id FROM items WHERE name = 'eggs'), 5.25),
    ((SELECT id FROM items WHERE name = 'chicken'), 8.99),
    ((SELECT id FROM items WHERE name = 'beef'), 12.99),
    ((SELECT id FROM items WHERE name = 'apples'), 2.99),
    ((SELECT id FROM items WHERE name = 'bananas'), 1.99),
    ((SELECT id FROM items WHERE name = 'soda'), 3.50),
    ((SELECT id FROM items WHERE name = 'napkins'), 4.99);