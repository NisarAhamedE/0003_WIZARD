-- Sample E-commerce Wizards with 6 steps and various option types

-- First, create a category for e-commerce
INSERT INTO wizard_categories (id, name, description, icon, display_order)
VALUES
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'E-Commerce', 'Online shopping and product configuration', 'shopping_cart', 1)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- WIZARD 1: Custom T-Shirt Builder
-- ============================================
INSERT INTO wizards (
    id, name, description, icon, cover_image, is_published,
    require_login, allow_anonymous, save_progress, show_progress_bar,
    estimated_time, difficulty_level, tags, category_id, created_by_id
)
VALUES (
    'w1000001-0000-0000-0000-000000000001',
    'Custom T-Shirt Designer',
    'Design your perfect custom t-shirt with our step-by-step configurator. Choose size, color, material, print options, and more!',
    'checkroom',
    NULL,
    true,
    true,
    false,
    true,
    true,
    15,
    'beginner',
    ARRAY['clothing', 't-shirt', 'custom', 'print'],
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    (SELECT id FROM users WHERE username = 'admin' LIMIT 1)
);

-- Step 1: Size Selection (Single Select)
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's1000001-0001-0000-0000-000000000001',
    'w1000001-0000-0000-0000-000000000001',
    'Select Your Size',
    'Choose the t-shirt size that fits you best',
    'Refer to our size chart if you are unsure about your measurements',
    1,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os100001-0001-0000-0000-000000000001',
    's1000001-0001-0000-0000-000000000001',
    'T-Shirt Size',
    'Select your preferred size',
    'single_select',
    true,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op100001-0001-0001-0000-000000000001', 'os100001-0001-0000-0000-000000000001', 'Small (S)', 'small', 'Chest: 34-36"', 0, 1),
    ('op100001-0001-0002-0000-000000000001', 'os100001-0001-0000-0000-000000000001', 'Medium (M)', 'medium', 'Chest: 38-40"', 0, 2),
    ('op100001-0001-0003-0000-000000000001', 'os100001-0001-0000-0000-000000000001', 'Large (L)', 'large', 'Chest: 42-44"', 0, 3),
    ('op100001-0001-0004-0000-000000000001', 'os100001-0001-0000-0000-000000000001', 'X-Large (XL)', 'xlarge', 'Chest: 46-48"', 2.00, 4),
    ('op100001-0001-0005-0000-000000000001', 'os100001-0001-0000-0000-000000000001', 'XX-Large (XXL)', 'xxlarge', 'Chest: 50-52"', 4.00, 5);

-- Step 2: Color Selection (Single Select with Colors)
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's1000001-0002-0000-0000-000000000001',
    'w1000001-0000-0000-0000-000000000001',
    'Choose Your Color',
    'Pick your favorite t-shirt color',
    'Popular colors include white, black, and navy blue',
    2,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os100001-0002-0000-0000-000000000001',
    's1000001-0002-0000-0000-000000000001',
    'T-Shirt Color',
    'Choose from our available colors',
    'single_select',
    true,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op100001-0002-0001-0000-000000000001', 'os100001-0002-0000-0000-000000000001', 'White', 'white', 'Classic white', 0, 1),
    ('op100001-0002-0002-0000-000000000001', 'os100001-0002-0000-0000-000000000001', 'Black', 'black', 'Solid black', 0, 2),
    ('op100001-0002-0003-0000-000000000001', 'os100001-0002-0000-0000-000000000001', 'Navy Blue', 'navy', 'Deep navy blue', 0, 3),
    ('op100001-0002-0004-0000-000000000001', 'os100001-0002-0000-0000-000000000001', 'Red', 'red', 'Vibrant red', 1.50, 4),
    ('op100001-0002-0005-0000-000000000001', 'os100001-0002-0000-0000-000000000001', 'Forest Green', 'green', 'Natural forest green', 1.50, 5),
    ('op100001-0002-0006-0000-000000000001', 'os100001-0002-0000-0000-000000000001', 'Heather Gray', 'gray', 'Soft heather gray', 2.00, 6);

-- Step 3: Material Type (Single Select)
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's1000001-0003-0000-0000-000000000001',
    'w1000001-0000-0000-0000-000000000001',
    'Select Material',
    'Choose the fabric type for comfort and durability',
    'Cotton is breathable, polyester is moisture-wicking, blend offers both benefits',
    3,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os100001-0003-0000-0000-000000000001',
    's1000001-0003-0000-0000-000000000001',
    'Fabric Material',
    'Select your preferred material',
    'single_select',
    true,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op100001-0003-0001-0000-000000000001', 'os100001-0003-0000-0000-000000000001', '100% Cotton', 'cotton', 'Natural, breathable, soft', 0, 1),
    ('op100001-0003-0002-0000-000000000001', 'os100001-0003-0000-0000-000000000001', 'Polyester Blend', 'polyester_blend', '60% Cotton, 40% Polyester - wrinkle resistant', 3.00, 2),
    ('op100001-0003-0003-0000-000000000001', 'os100001-0003-0000-0000-000000000001', 'Tri-Blend', 'tri_blend', '50% Poly, 25% Cotton, 25% Rayon - ultra soft', 5.00, 3),
    ('op100001-0003-0004-0000-000000000001', 'os100001-0003-0000-0000-000000000001', 'Organic Cotton', 'organic', '100% certified organic cotton', 8.00, 4);

-- Step 4: Print Options (Multiple Select)
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's1000001-0004-0000-0000-000000000001',
    'w1000001-0000-0000-0000-000000000001',
    'Print Locations',
    'Select where you want your design printed',
    'You can select multiple print locations for a fully customized look',
    4,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, min_selections, max_selections, display_order)
VALUES (
    'os100001-0004-0000-0000-000000000001',
    's1000001-0004-0000-0000-000000000001',
    'Print Locations',
    'Choose one or more print areas',
    'multiple_select',
    true,
    1,
    4,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op100001-0004-0001-0000-000000000001', 'os100001-0004-0000-0000-000000000001', 'Front Center', 'front_center', 'Large print on front chest', 10.00, 1),
    ('op100001-0004-0002-0000-000000000001', 'os100001-0004-0000-0000-000000000001', 'Back Full', 'back_full', 'Full back print', 12.00, 2),
    ('op100001-0004-0003-0000-000000000001', 'os100001-0004-0000-0000-000000000001', 'Left Sleeve', 'left_sleeve', 'Small print on left sleeve', 5.00, 3),
    ('op100001-0004-0004-0000-000000000001', 'os100001-0004-0000-0000-000000000001', 'Right Sleeve', 'right_sleeve', 'Small print on right sleeve', 5.00, 4),
    ('op100001-0004-0005-0000-000000000001', 'os100001-0004-0000-0000-000000000001', 'Pocket Area', 'pocket', 'Small logo on pocket area', 4.00, 5);

-- Step 5: Custom Text and Rating
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's1000001-0005-0000-0000-000000000001',
    'w1000001-0000-0000-0000-000000000001',
    'Personalization',
    'Add your custom text and preferences',
    'Enter any text you want printed on your t-shirt',
    5,
    false
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, placeholder, help_text, display_order)
VALUES (
    'os100001-0005-0001-0000-000000000001',
    's1000001-0005-0000-0000-000000000001',
    'Custom Text',
    'Enter text to be printed (max 50 characters)',
    'text_input',
    false,
    'Enter your custom text here...',
    'Text will be printed in the location you selected',
    1
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os100001-0005-0002-0000-000000000001',
    's1000001-0005-0000-0000-000000000001',
    'Design Importance',
    'How important is the design quality to you? (1-5)',
    'rating',
    false,
    2
);

-- Step 6: Quantity and Final Options
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's1000001-0006-0000-0000-000000000001',
    'w1000001-0000-0000-0000-000000000001',
    'Quantity & Checkout',
    'Select quantity and additional services',
    'Bulk orders over 10 items get 10% discount',
    6,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, min_value, max_value, step_increment, display_order)
VALUES (
    'os100001-0006-0001-0000-000000000001',
    's1000001-0006-0000-0000-000000000001',
    'Quantity',
    'How many t-shirts do you want?',
    'number_input',
    true,
    1,
    100,
    1,
    1
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os100001-0006-0002-0000-000000000001',
    's1000001-0006-0000-0000-000000000001',
    'Additional Services',
    'Select any additional services',
    'multiple_select',
    false,
    2
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op100001-0006-0001-0000-000000000001', 'os100001-0006-0002-0000-000000000001', 'Gift Wrapping', 'gift_wrap', 'Premium gift wrapping', 5.00, 1),
    ('op100001-0006-0002-0000-000000000001', 'os100001-0006-0002-0000-000000000001', 'Express Shipping', 'express_ship', '2-day express delivery', 15.00, 2),
    ('op100001-0006-0003-0000-000000000001', 'os100001-0006-0002-0000-000000000001', 'Design Proof', 'design_proof', 'Email proof before printing', 3.00, 3),
    ('op100001-0006-0004-0000-000000000001', 'os100001-0006-0002-0000-000000000001', 'Insurance', 'insurance', 'Shipping insurance coverage', 7.00, 4);


-- ============================================
-- WIZARD 2: Custom Laptop Configurator
-- ============================================
INSERT INTO wizards (
    id, name, description, icon, cover_image, is_published,
    require_login, allow_anonymous, save_progress, show_progress_bar,
    estimated_time, difficulty_level, tags, category_id, created_by_id
)
VALUES (
    'w2000002-0000-0000-0000-000000000002',
    'Laptop Configuration Wizard',
    'Build your perfect laptop by choosing processor, RAM, storage, display, and accessories. Get the exact specifications you need!',
    'laptop',
    NULL,
    true,
    true,
    false,
    true,
    true,
    20,
    'intermediate',
    ARRAY['electronics', 'laptop', 'computer', 'custom-build'],
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    (SELECT id FROM users WHERE username = 'admin' LIMIT 1)
);

-- Step 1: Processor Selection
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's2000002-0001-0000-0000-000000000002',
    'w2000002-0000-0000-0000-000000000002',
    'Choose Processor',
    'Select the CPU that powers your laptop',
    'Higher core count and clock speed means better performance for demanding tasks',
    1,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os200002-0001-0000-0000-000000000002',
    's2000002-0001-0000-0000-000000000002',
    'Processor (CPU)',
    'Choose your processor',
    'single_select',
    true,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op200002-0001-0001-0000-000000000002', 'os200002-0001-0000-0000-000000000002', 'Intel Core i5-13400', 'i5_13400', '10 cores, up to 4.6GHz - Great for everyday tasks', 0, 1),
    ('op200002-0001-0002-0000-000000000002', 'os200002-0001-0000-0000-000000000002', 'Intel Core i7-13700', 'i7_13700', '16 cores, up to 5.2GHz - Excellent for multitasking', 150.00, 2),
    ('op200002-0001-0003-0000-000000000002', 'os200002-0001-0000-0000-000000000002', 'Intel Core i9-13900', 'i9_13900', '24 cores, up to 5.8GHz - Maximum performance', 350.00, 3),
    ('op200002-0001-0004-0000-000000000002', 'os200002-0001-0000-0000-000000000002', 'AMD Ryzen 7 7800X', 'ryzen7_7800x', '8 cores, up to 5.0GHz - Great efficiency', 120.00, 4),
    ('op200002-0001-0005-0000-000000000002', 'os200002-0001-0000-0000-000000000002', 'AMD Ryzen 9 7950X', 'ryzen9_7950x', '16 cores, up to 5.7GHz - Powerhouse CPU', 380.00, 5);

-- Step 2: RAM Selection
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's2000002-0002-0000-0000-000000000002',
    'w2000002-0000-0000-0000-000000000002',
    'Select Memory (RAM)',
    'Choose how much RAM you need',
    '16GB is recommended for most users, 32GB+ for professionals',
    2,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os200002-0002-0000-0000-000000000002',
    's2000002-0002-0000-0000-000000000002',
    'RAM Capacity',
    'Select memory size',
    'single_select',
    true,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op200002-0002-0001-0000-000000000002', 'os200002-0002-0000-0000-000000000002', '8GB DDR5', '8gb', 'Basic usage - web browsing, documents', 0, 1),
    ('op200002-0002-0002-0000-000000000002', 'os200002-0002-0000-0000-000000000002', '16GB DDR5', '16gb', 'Recommended - smooth multitasking', 80.00, 2),
    ('op200002-0002-0003-0000-000000000002', 'os200002-0002-0000-0000-000000000002', '32GB DDR5', '32gb', 'Professional - video editing, development', 180.00, 3),
    ('op200002-0002-0004-0000-000000000002', 'os200002-0002-0000-0000-000000000002', '64GB DDR5', '64gb', 'Extreme - 3D rendering, data science', 400.00, 4);

-- Step 3: Storage Configuration
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's2000002-0003-0000-0000-000000000002',
    'w2000002-0000-0000-0000-000000000002',
    'Storage Options',
    'Configure your storage drives',
    'NVMe SSDs offer fastest speeds, you can add multiple drives',
    3,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os200002-0003-0001-0000-000000000002',
    's2000002-0003-0000-0000-000000000002',
    'Primary Storage',
    'Main SSD drive',
    'single_select',
    true,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op200002-0003-0001-0000-000000000002', 'os200002-0003-0001-0000-000000000002', '256GB NVMe SSD', '256gb_nvme', 'Basic storage', 0, 1),
    ('op200002-0003-0002-0000-000000000002', 'os200002-0003-0001-0000-000000000002', '512GB NVMe SSD', '512gb_nvme', 'Standard storage', 60.00, 2),
    ('op200002-0003-0003-0000-000000000002', 'os200002-0003-0001-0000-000000000002', '1TB NVMe SSD', '1tb_nvme', 'Ample storage', 120.00, 3),
    ('op200002-0003-0004-0000-000000000002', 'os200002-0003-0001-0000-000000000002', '2TB NVMe SSD', '2tb_nvme', 'Plenty of space', 250.00, 4);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os200002-0003-0002-0000-000000000002',
    's2000002-0003-0000-0000-000000000002',
    'Secondary Storage (Optional)',
    'Add extra storage',
    'single_select',
    false,
    2
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op200002-0003-0005-0000-000000000002', 'os200002-0003-0002-0000-000000000002', 'None', 'none', 'No secondary drive', 0, 1),
    ('op200002-0003-0006-0000-000000000002', 'os200002-0003-0002-0000-000000000002', '1TB HDD', '1tb_hdd', 'Budget extra storage', 50.00, 2),
    ('op200002-0003-0007-0000-000000000002', 'os200002-0003-0002-0000-000000000002', '2TB HDD', '2tb_hdd', 'Large extra storage', 80.00, 3),
    ('op200002-0003-0008-0000-000000000002', 'os200002-0003-0002-0000-000000000002', '1TB NVMe SSD', '1tb_nvme_secondary', 'Fast extra storage', 130.00, 4);

-- Step 4: Display Options
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's2000002-0004-0000-0000-000000000002',
    'w2000002-0000-0000-0000-000000000002',
    'Display Configuration',
    'Choose your screen specifications',
    'Higher resolution and refresh rate provide better visual experience',
    4,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os200002-0004-0000-0000-000000000002',
    's2000002-0004-0000-0000-000000000002',
    'Display Type',
    'Select screen specifications',
    'single_select',
    true,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op200002-0004-0001-0000-000000000002', 'os200002-0004-0000-0000-000000000002', '15.6" FHD 60Hz', '15_fhd_60', '1920x1080, standard refresh rate', 0, 1),
    ('op200002-0004-0002-0000-000000000002', 'os200002-0004-0000-0000-000000000002', '15.6" FHD 144Hz', '15_fhd_144', '1920x1080, smooth gaming', 100.00, 2),
    ('op200002-0004-0003-0000-000000000002', 'os200002-0004-0000-0000-000000000002', '15.6" QHD 165Hz', '15_qhd_165', '2560x1440, crisp and smooth', 200.00, 3),
    ('op200002-0004-0004-0000-000000000002', 'os200002-0004-0000-0000-000000000002', '16" 4K OLED', '16_4k_oled', '3840x2160, stunning colors', 450.00, 4),
    ('op200002-0004-0005-0000-000000000002', 'os200002-0004-0000-0000-000000000002', '17.3" QHD 240Hz', '17_qhd_240', 'Large screen, ultra smooth', 350.00, 5);

-- Step 5: Software and Features
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's2000002-0005-0000-0000-000000000002',
    'w2000002-0000-0000-0000-000000000002',
    'Software & Features',
    'Select operating system and additional features',
    'Choose the software bundle that fits your workflow',
    5,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os200002-0005-0001-0000-000000000002',
    's2000002-0005-0000-0000-000000000002',
    'Operating System',
    'Pre-installed OS',
    'single_select',
    true,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op200002-0005-0001-0000-000000000002', 'os200002-0005-0001-0000-000000000002', 'Windows 11 Home', 'win11_home', 'Standard Windows experience', 0, 1),
    ('op200002-0005-0002-0000-000000000002', 'os200002-0005-0001-0000-000000000002', 'Windows 11 Pro', 'win11_pro', 'Advanced features for professionals', 50.00, 2),
    ('op200002-0005-0003-0000-000000000002', 'os200002-0005-0001-0000-000000000002', 'Ubuntu Linux', 'ubuntu', 'Free open-source OS', -20.00, 3),
    ('op200002-0005-0004-0000-000000000002', 'os200002-0005-0001-0000-000000000002', 'No OS (FreeDOS)', 'freedos', 'Install your own OS', -50.00, 4);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os200002-0005-0002-0000-000000000002',
    's2000002-0005-0000-0000-000000000002',
    'Additional Software',
    'Select software bundles',
    'multiple_select',
    false,
    2
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op200002-0005-0005-0000-000000000002', 'os200002-0005-0002-0000-000000000002', 'Microsoft Office 365', 'office365', 'Word, Excel, PowerPoint, Outlook', 99.00, 1),
    ('op200002-0005-0006-0000-000000000002', 'os200002-0005-0002-0000-000000000002', 'Adobe Creative Suite', 'adobe_cc', 'Photoshop, Illustrator, Premiere', 299.00, 2),
    ('op200002-0005-0007-0000-000000000002', 'os200002-0005-0002-0000-000000000002', 'Antivirus Pro (3yr)', 'antivirus', 'Premium security protection', 79.00, 3),
    ('op200002-0005-0008-0000-000000000002', 'os200002-0005-0002-0000-000000000002', 'VPN Service (1yr)', 'vpn', 'Secure internet connection', 49.00, 4);

-- Step 6: Accessories and Warranty
INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
VALUES (
    's2000002-0006-0000-0000-000000000002',
    'w2000002-0000-0000-0000-000000000002',
    'Accessories & Warranty',
    'Add accessories and warranty protection',
    'Protect your investment with extended warranty',
    6,
    true
);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os200002-0006-0001-0000-000000000002',
    's2000002-0006-0000-0000-000000000002',
    'Warranty Plan',
    'Extended warranty options',
    'single_select',
    true,
    1
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op200002-0006-0001-0000-000000000002', 'os200002-0006-0001-0000-000000000002', 'Standard 1 Year', 'warranty_1yr', 'Basic manufacturer warranty', 0, 1),
    ('op200002-0006-0002-0000-000000000002', 'os200002-0006-0001-0000-000000000002', 'Extended 2 Years', 'warranty_2yr', 'Extra year of coverage', 99.00, 2),
    ('op200002-0006-0003-0000-000000000002', 'os200002-0006-0001-0000-000000000002', 'Premium 3 Years', 'warranty_3yr', 'Full 3-year protection', 179.00, 3),
    ('op200002-0006-0004-0000-000000000002', 'os200002-0006-0001-0000-000000000002', 'Ultimate 4 Years + Accidental', 'warranty_4yr_acc', 'Includes accidental damage', 299.00, 4);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
VALUES (
    'os200002-0006-0002-0000-000000000002',
    's2000002-0006-0000-0000-000000000002',
    'Accessories',
    'Add useful accessories',
    'multiple_select',
    false,
    2
);

INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
    ('op200002-0006-0005-0000-000000000002', 'os200002-0006-0002-0000-000000000002', 'Laptop Bag', 'laptop_bag', 'Premium protective carrying case', 49.00, 1),
    ('op200002-0006-0006-0000-000000000002', 'os200002-0006-0002-0000-000000000002', 'Wireless Mouse', 'wireless_mouse', 'Ergonomic wireless mouse', 29.00, 2),
    ('op200002-0006-0007-0000-000000000002', 'os200002-0006-0002-0000-000000000002', 'USB-C Hub', 'usbc_hub', '7-in-1 USB-C docking station', 79.00, 3),
    ('op200002-0006-0008-0000-000000000002', 'os200002-0006-0002-0000-000000000002', 'External Webcam 4K', 'webcam_4k', 'High-quality video calls', 99.00, 4),
    ('op200002-0006-0009-0000-000000000002', 'os200002-0006-0002-0000-000000000002', 'Laptop Stand', 'laptop_stand', 'Ergonomic aluminum stand', 59.00, 5);

INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, placeholder, help_text, display_order)
VALUES (
    'os200002-0006-0003-0000-000000000002',
    's2000002-0006-0000-0000-000000000002',
    'Special Instructions',
    'Any special requests or notes for your order',
    'text_input',
    false,
    'Enter any special instructions here...',
    'We will do our best to accommodate your requests',
    3
);

-- Update wizard session counts (optional, for display purposes)
UPDATE wizards SET total_sessions = 0, completed_sessions = 0 WHERE id IN (
    'w1000001-0000-0000-0000-000000000001',
    'w2000002-0000-0000-0000-000000000002'
);
