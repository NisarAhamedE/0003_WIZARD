-- Sample E-commerce Wizards - Fixed version

-- Get the admin user id
DO $$
DECLARE
    admin_id uuid;
    cat_id uuid := 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
    w1_id uuid := '11111111-1111-1111-1111-111111111111';
    w2_id uuid := '22222222-2222-2222-2222-222222222222';
BEGIN
    -- Get admin user
    SELECT id INTO admin_id FROM users WHERE username = 'admin' LIMIT 1;

    -- Create category if not exists or get existing
    INSERT INTO wizard_categories (id, name, description, icon, display_order)
    VALUES (cat_id, 'E-Commerce', 'Online shopping and product configuration', 'shopping_cart', 1)
    ON CONFLICT (name) DO UPDATE SET id = wizard_categories.id
    RETURNING id INTO cat_id;

    -- ============================================
    -- WIZARD 1: Custom T-Shirt Builder
    -- ============================================
    INSERT INTO wizards (
        id, name, description, icon, is_published,
        require_login, allow_anonymous, auto_save,
        estimated_time, difficulty_level, tags, category_id, created_by
    ) VALUES (
        w1_id,
        'Custom T-Shirt Designer',
        'Design your perfect custom t-shirt with our step-by-step configurator. Choose size, color, material, print options, and more!',
        'checkroom',
        true,
        true,
        false,
        true,
        15,
        'easy',
        '["clothing", "t-shirt", "custom", "print"]'::jsonb,
        cat_id,
        admin_id
    );

    -- Step 1: Size Selection
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '11111111-0001-0001-0001-111111111111',
        w1_id,
        'Select Your Size',
        'Choose the t-shirt size that fits you best',
        'Refer to our size chart if you are unsure about your measurements',
        1,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '11111111-0001-0001-0001-aaaaaaaaaaaa',
        '11111111-0001-0001-0001-111111111111',
        'T-Shirt Size',
        'Select your preferred size',
        'single_select',
        true,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('11111111-0001-0001-0001-000000000001', '11111111-0001-0001-0001-aaaaaaaaaaaa', 'Small (S)', 'small', 'Chest: 34-36"', 0, 1),
        ('11111111-0001-0001-0001-000000000002', '11111111-0001-0001-0001-aaaaaaaaaaaa', 'Medium (M)', 'medium', 'Chest: 38-40"', 0, 2),
        ('11111111-0001-0001-0001-000000000003', '11111111-0001-0001-0001-aaaaaaaaaaaa', 'Large (L)', 'large', 'Chest: 42-44"', 0, 3),
        ('11111111-0001-0001-0001-000000000004', '11111111-0001-0001-0001-aaaaaaaaaaaa', 'X-Large (XL)', 'xlarge', 'Chest: 46-48"', 2.00, 4),
        ('11111111-0001-0001-0001-000000000005', '11111111-0001-0001-0001-aaaaaaaaaaaa', 'XX-Large (XXL)', 'xxlarge', 'Chest: 50-52"', 4.00, 5);

    -- Step 2: Color Selection
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '11111111-0002-0002-0002-111111111111',
        w1_id,
        'Choose Your Color',
        'Pick your favorite t-shirt color',
        'Popular colors include white, black, and navy blue',
        2,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '11111111-0002-0002-0002-aaaaaaaaaaaa',
        '11111111-0002-0002-0002-111111111111',
        'T-Shirt Color',
        'Choose from our available colors',
        'single_select',
        true,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('11111111-0002-0002-0002-000000000001', '11111111-0002-0002-0002-aaaaaaaaaaaa', 'White', 'white', 'Classic white', 0, 1),
        ('11111111-0002-0002-0002-000000000002', '11111111-0002-0002-0002-aaaaaaaaaaaa', 'Black', 'black', 'Solid black', 0, 2),
        ('11111111-0002-0002-0002-000000000003', '11111111-0002-0002-0002-aaaaaaaaaaaa', 'Navy Blue', 'navy', 'Deep navy blue', 0, 3),
        ('11111111-0002-0002-0002-000000000004', '11111111-0002-0002-0002-aaaaaaaaaaaa', 'Red', 'red', 'Vibrant red', 1.50, 4),
        ('11111111-0002-0002-0002-000000000005', '11111111-0002-0002-0002-aaaaaaaaaaaa', 'Forest Green', 'green', 'Natural forest green', 1.50, 5);

    -- Step 3: Material Type
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '11111111-0003-0003-0003-111111111111',
        w1_id,
        'Select Material',
        'Choose the fabric type for comfort and durability',
        'Cotton is breathable, polyester is moisture-wicking',
        3,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '11111111-0003-0003-0003-aaaaaaaaaaaa',
        '11111111-0003-0003-0003-111111111111',
        'Fabric Material',
        'Select your preferred material',
        'single_select',
        true,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('11111111-0003-0003-0003-000000000001', '11111111-0003-0003-0003-aaaaaaaaaaaa', '100% Cotton', 'cotton', 'Natural, breathable, soft', 0, 1),
        ('11111111-0003-0003-0003-000000000002', '11111111-0003-0003-0003-aaaaaaaaaaaa', 'Polyester Blend', 'polyester_blend', '60% Cotton, 40% Polyester', 3.00, 2),
        ('11111111-0003-0003-0003-000000000003', '11111111-0003-0003-0003-aaaaaaaaaaaa', 'Tri-Blend', 'tri_blend', '50% Poly, 25% Cotton, 25% Rayon', 5.00, 3),
        ('11111111-0003-0003-0003-000000000004', '11111111-0003-0003-0003-aaaaaaaaaaaa', 'Organic Cotton', 'organic', '100% certified organic', 8.00, 4);

    -- Step 4: Print Options (Multiple Select)
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '11111111-0004-0004-0004-111111111111',
        w1_id,
        'Print Locations',
        'Select where you want your design printed',
        'You can select multiple print locations',
        4,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, min_selections, max_selections, display_order)
    VALUES (
        '11111111-0004-0004-0004-aaaaaaaaaaaa',
        '11111111-0004-0004-0004-111111111111',
        'Print Locations',
        'Choose one or more print areas',
        'multiple_select',
        true,
        1,
        4,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('11111111-0004-0004-0004-000000000001', '11111111-0004-0004-0004-aaaaaaaaaaaa', 'Front Center', 'front_center', 'Large print on front chest', 10.00, 1),
        ('11111111-0004-0004-0004-000000000002', '11111111-0004-0004-0004-aaaaaaaaaaaa', 'Back Full', 'back_full', 'Full back print', 12.00, 2),
        ('11111111-0004-0004-0004-000000000003', '11111111-0004-0004-0004-aaaaaaaaaaaa', 'Left Sleeve', 'left_sleeve', 'Small print on left sleeve', 5.00, 3),
        ('11111111-0004-0004-0004-000000000004', '11111111-0004-0004-0004-aaaaaaaaaaaa', 'Right Sleeve', 'right_sleeve', 'Small print on right sleeve', 5.00, 4);

    -- Step 5: Custom Text
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '11111111-0005-0005-0005-111111111111',
        w1_id,
        'Personalization',
        'Add your custom text and preferences',
        'Enter any text you want printed on your t-shirt',
        5,
        false
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, placeholder, help_text, display_order)
    VALUES (
        '11111111-0005-0005-0005-aaaaaaaaaaaa',
        '11111111-0005-0005-0005-111111111111',
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
        '11111111-0005-0005-0005-bbbbbbbbbbbb',
        '11111111-0005-0005-0005-111111111111',
        'Design Importance',
        'How important is the design quality to you? (1-5)',
        'rating',
        false,
        2
    );

    -- Step 6: Quantity
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '11111111-0006-0006-0006-111111111111',
        w1_id,
        'Quantity & Checkout',
        'Select quantity and additional services',
        'Bulk orders over 10 items get 10% discount',
        6,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, min_value, max_value, step_increment, display_order)
    VALUES (
        '11111111-0006-0006-0006-aaaaaaaaaaaa',
        '11111111-0006-0006-0006-111111111111',
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
        '11111111-0006-0006-0006-bbbbbbbbbbbb',
        '11111111-0006-0006-0006-111111111111',
        'Additional Services',
        'Select any additional services',
        'multiple_select',
        false,
        2
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('11111111-0006-0006-0006-000000000001', '11111111-0006-0006-0006-bbbbbbbbbbbb', 'Gift Wrapping', 'gift_wrap', 'Premium gift wrapping', 5.00, 1),
        ('11111111-0006-0006-0006-000000000002', '11111111-0006-0006-0006-bbbbbbbbbbbb', 'Express Shipping', 'express_ship', '2-day express delivery', 15.00, 2),
        ('11111111-0006-0006-0006-000000000003', '11111111-0006-0006-0006-bbbbbbbbbbbb', 'Design Proof', 'design_proof', 'Email proof before printing', 3.00, 3);

    -- ============================================
    -- WIZARD 2: Custom Laptop Configurator
    -- ============================================
    INSERT INTO wizards (
        id, name, description, icon, is_published,
        require_login, allow_anonymous, auto_save,
        estimated_time, difficulty_level, tags, category_id, created_by
    ) VALUES (
        w2_id,
        'Laptop Configuration Wizard',
        'Build your perfect laptop by choosing processor, RAM, storage, display, and accessories. Get the exact specifications you need!',
        'laptop',
        true,
        true,
        false,
        true,
        20,
        'medium',
        '["electronics", "laptop", "computer", "custom-build"]'::jsonb,
        cat_id,
        admin_id
    );

    -- Step 1: Processor Selection
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '22222222-0001-0001-0001-222222222222',
        w2_id,
        'Choose Processor',
        'Select the CPU that powers your laptop',
        'Higher core count means better performance',
        1,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '22222222-0001-0001-0001-aaaaaaaaaaaa',
        '22222222-0001-0001-0001-222222222222',
        'Processor (CPU)',
        'Choose your processor',
        'single_select',
        true,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('22222222-0001-0001-0001-000000000001', '22222222-0001-0001-0001-aaaaaaaaaaaa', 'Intel Core i5-13400', 'i5_13400', '10 cores, up to 4.6GHz', 0, 1),
        ('22222222-0001-0001-0001-000000000002', '22222222-0001-0001-0001-aaaaaaaaaaaa', 'Intel Core i7-13700', 'i7_13700', '16 cores, up to 5.2GHz', 150.00, 2),
        ('22222222-0001-0001-0001-000000000003', '22222222-0001-0001-0001-aaaaaaaaaaaa', 'Intel Core i9-13900', 'i9_13900', '24 cores, up to 5.8GHz', 350.00, 3),
        ('22222222-0001-0001-0001-000000000004', '22222222-0001-0001-0001-aaaaaaaaaaaa', 'AMD Ryzen 7 7800X', 'ryzen7_7800x', '8 cores, up to 5.0GHz', 120.00, 4);

    -- Step 2: RAM Selection
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '22222222-0002-0002-0002-222222222222',
        w2_id,
        'Select Memory (RAM)',
        'Choose how much RAM you need',
        '16GB is recommended for most users',
        2,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '22222222-0002-0002-0002-aaaaaaaaaaaa',
        '22222222-0002-0002-0002-222222222222',
        'RAM Capacity',
        'Select memory size',
        'single_select',
        true,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('22222222-0002-0002-0002-000000000001', '22222222-0002-0002-0002-aaaaaaaaaaaa', '8GB DDR5', '8gb', 'Basic usage', 0, 1),
        ('22222222-0002-0002-0002-000000000002', '22222222-0002-0002-0002-aaaaaaaaaaaa', '16GB DDR5', '16gb', 'Recommended', 80.00, 2),
        ('22222222-0002-0002-0002-000000000003', '22222222-0002-0002-0002-aaaaaaaaaaaa', '32GB DDR5', '32gb', 'Professional', 180.00, 3),
        ('22222222-0002-0002-0002-000000000004', '22222222-0002-0002-0002-aaaaaaaaaaaa', '64GB DDR5', '64gb', 'Extreme', 400.00, 4);

    -- Step 3: Storage
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '22222222-0003-0003-0003-222222222222',
        w2_id,
        'Storage Options',
        'Configure your storage drives',
        'NVMe SSDs offer fastest speeds',
        3,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '22222222-0003-0003-0003-aaaaaaaaaaaa',
        '22222222-0003-0003-0003-222222222222',
        'Primary Storage',
        'Main SSD drive',
        'single_select',
        true,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('22222222-0003-0003-0003-000000000001', '22222222-0003-0003-0003-aaaaaaaaaaaa', '256GB NVMe SSD', '256gb_nvme', 'Basic storage', 0, 1),
        ('22222222-0003-0003-0003-000000000002', '22222222-0003-0003-0003-aaaaaaaaaaaa', '512GB NVMe SSD', '512gb_nvme', 'Standard storage', 60.00, 2),
        ('22222222-0003-0003-0003-000000000003', '22222222-0003-0003-0003-aaaaaaaaaaaa', '1TB NVMe SSD', '1tb_nvme', 'Ample storage', 120.00, 3),
        ('22222222-0003-0003-0003-000000000004', '22222222-0003-0003-0003-aaaaaaaaaaaa', '2TB NVMe SSD', '2tb_nvme', 'Plenty of space', 250.00, 4);

    -- Step 4: Display
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '22222222-0004-0004-0004-222222222222',
        w2_id,
        'Display Configuration',
        'Choose your screen specifications',
        'Higher resolution provides better visuals',
        4,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '22222222-0004-0004-0004-aaaaaaaaaaaa',
        '22222222-0004-0004-0004-222222222222',
        'Display Type',
        'Select screen specifications',
        'single_select',
        true,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('22222222-0004-0004-0004-000000000001', '22222222-0004-0004-0004-aaaaaaaaaaaa', '15.6" FHD 60Hz', '15_fhd_60', '1920x1080, standard', 0, 1),
        ('22222222-0004-0004-0004-000000000002', '22222222-0004-0004-0004-aaaaaaaaaaaa', '15.6" FHD 144Hz', '15_fhd_144', '1920x1080, smooth', 100.00, 2),
        ('22222222-0004-0004-0004-000000000003', '22222222-0004-0004-0004-aaaaaaaaaaaa', '15.6" QHD 165Hz', '15_qhd_165', '2560x1440, crisp', 200.00, 3),
        ('22222222-0004-0004-0004-000000000004', '22222222-0004-0004-0004-aaaaaaaaaaaa', '16" 4K OLED', '16_4k_oled', '3840x2160, stunning', 450.00, 4);

    -- Step 5: Software
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '22222222-0005-0005-0005-222222222222',
        w2_id,
        'Software & Features',
        'Select operating system and software',
        'Choose the software bundle that fits your workflow',
        5,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '22222222-0005-0005-0005-aaaaaaaaaaaa',
        '22222222-0005-0005-0005-222222222222',
        'Operating System',
        'Pre-installed OS',
        'single_select',
        true,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('22222222-0005-0005-0005-000000000001', '22222222-0005-0005-0005-aaaaaaaaaaaa', 'Windows 11 Home', 'win11_home', 'Standard Windows', 0, 1),
        ('22222222-0005-0005-0005-000000000002', '22222222-0005-0005-0005-aaaaaaaaaaaa', 'Windows 11 Pro', 'win11_pro', 'Advanced features', 50.00, 2),
        ('22222222-0005-0005-0005-000000000003', '22222222-0005-0005-0005-aaaaaaaaaaaa', 'Ubuntu Linux', 'ubuntu', 'Free open-source OS', -20.00, 3);

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '22222222-0005-0005-0005-bbbbbbbbbbbb',
        '22222222-0005-0005-0005-222222222222',
        'Additional Software',
        'Select software bundles',
        'multiple_select',
        false,
        2
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('22222222-0005-0005-0005-000000000004', '22222222-0005-0005-0005-bbbbbbbbbbbb', 'Microsoft Office 365', 'office365', 'Word, Excel, PowerPoint', 99.00, 1),
        ('22222222-0005-0005-0005-000000000005', '22222222-0005-0005-0005-bbbbbbbbbbbb', 'Adobe Creative Suite', 'adobe_cc', 'Photoshop, Illustrator', 299.00, 2),
        ('22222222-0005-0005-0005-000000000006', '22222222-0005-0005-0005-bbbbbbbbbbbb', 'Antivirus Pro (3yr)', 'antivirus', 'Security protection', 79.00, 3);

    -- Step 6: Warranty and Accessories
    INSERT INTO steps (id, wizard_id, name, description, help_text, step_order, is_required)
    VALUES (
        '22222222-0006-0006-0006-222222222222',
        w2_id,
        'Accessories & Warranty',
        'Add accessories and warranty protection',
        'Protect your investment with extended warranty',
        6,
        true
    );

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '22222222-0006-0006-0006-aaaaaaaaaaaa',
        '22222222-0006-0006-0006-222222222222',
        'Warranty Plan',
        'Extended warranty options',
        'single_select',
        true,
        1
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('22222222-0006-0006-0006-000000000001', '22222222-0006-0006-0006-aaaaaaaaaaaa', 'Standard 1 Year', 'warranty_1yr', 'Basic warranty', 0, 1),
        ('22222222-0006-0006-0006-000000000002', '22222222-0006-0006-0006-aaaaaaaaaaaa', 'Extended 2 Years', 'warranty_2yr', 'Extra year', 99.00, 2),
        ('22222222-0006-0006-0006-000000000003', '22222222-0006-0006-0006-aaaaaaaaaaaa', 'Premium 3 Years', 'warranty_3yr', 'Full 3-year', 179.00, 3);

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, display_order)
    VALUES (
        '22222222-0006-0006-0006-bbbbbbbbbbbb',
        '22222222-0006-0006-0006-222222222222',
        'Accessories',
        'Add useful accessories',
        'multiple_select',
        false,
        2
    );

    INSERT INTO options (id, option_set_id, label, value, description, price, display_order) VALUES
        ('22222222-0006-0006-0006-000000000004', '22222222-0006-0006-0006-bbbbbbbbbbbb', 'Laptop Bag', 'laptop_bag', 'Premium carrying case', 49.00, 1),
        ('22222222-0006-0006-0006-000000000005', '22222222-0006-0006-0006-bbbbbbbbbbbb', 'Wireless Mouse', 'wireless_mouse', 'Ergonomic mouse', 29.00, 2),
        ('22222222-0006-0006-0006-000000000006', '22222222-0006-0006-0006-bbbbbbbbbbbb', 'USB-C Hub', 'usbc_hub', '7-in-1 docking station', 79.00, 3),
        ('22222222-0006-0006-0006-000000000007', '22222222-0006-0006-0006-bbbbbbbbbbbb', 'Laptop Stand', 'laptop_stand', 'Ergonomic stand', 59.00, 4);

    INSERT INTO option_sets (id, step_id, name, description, selection_type, is_required, placeholder, help_text, display_order)
    VALUES (
        '22222222-0006-0006-0006-cccccccccccc',
        '22222222-0006-0006-0006-222222222222',
        'Special Instructions',
        'Any special requests',
        'text_input',
        false,
        'Enter any special instructions here...',
        'We will do our best to accommodate',
        3
    );

END $$;
