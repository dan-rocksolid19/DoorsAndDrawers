-- Populate core_design table
INSERT INTO core_design (name, arch, created_at, updated_at) VALUES
    ('Crown', TRUE, datetime('now'), datetime('now')),
    ('Duncans', TRUE, datetime('now'), datetime('now')),
    ('French', TRUE, datetime('now'), datetime('now')),
    ('Heritage', TRUE, datetime('now'), datetime('now')),
    ('Oval', TRUE, datetime('now'), datetime('now')),
    ('Provincial', TRUE, datetime('now'), datetime('now')),
    ('Square', FALSE, datetime('now'), datetime('now'));

-- Populate core_edgeprofile table
INSERT INTO core_edgeprofile (name, created_at, updated_at) VALUES
    ('E1', datetime('now'), datetime('now')),
    ('E2', datetime('now'), datetime('now')),
    ('E3', datetime('now'), datetime('now')),
    ('E4', datetime('now'), datetime('now')),
    ('E5', datetime('now'), datetime('now')),
    ('E6', datetime('now'), datetime('now'));

-- Populate core_panelrise table
INSERT INTO core_panelrise (name, created_at, updated_at) VALUES
    ('PanelRaise1', datetime('now'), datetime('now')),
    ('PanelRaise2', datetime('now'), datetime('now')),
    ('PanelRaise3', datetime('now'), datetime('now'));

-- Populate core_paneltype table
INSERT INTO core_paneltype (name, surcharge_width, surcharge_height, surcharge_percent, minimum_sq_ft, use_flat_panel_price, created_at, updated_at) VALUES
    ('Drawer Front', 28, 10, 15, 0.8, FALSE, datetime('now'), datetime('now')),
    ('Flat Panel', 22, 39, 15, 2, TRUE, datetime('now'), datetime('now')),
    ('Frame Only', 22, 39, 15, 2, TRUE, datetime('now'), datetime('now')),
    ('Raised Panel', 22, 39, 15, 2, FALSE, datetime('now'), datetime('now')),
    ('Slab', 22, 39, 15, 2, TRUE, datetime('now'), datetime('now'));

-- Populate core_woodstock table
INSERT INTO core_woodstock (name, raised_panel_price, flat_panel_price, created_at, updated_at) VALUES
    ('Alder', 7.50, 7.00, datetime('now'), datetime('now')),
    ('Ash', 5.00, 4.50, datetime('now'), datetime('now')),
    ('Basswood', 5.00, 4.50, datetime('now'), datetime('now')),
    ('Birch', 6.50, 6.00, datetime('now'), datetime('now')),
    ('Cherry', 8.50, 8.00, datetime('now'), datetime('now')),
    ('Cypress', 8.50, 8.00, datetime('now'), datetime('now')),
    ('Hickory', 6.50, 6.00, datetime('now'), datetime('now')),
    ('Mahogany', 9.50, 9.00, datetime('now'), datetime('now')),
    ('Red Oak', 5.00, 4.50, datetime('now'), datetime('now'));

-- Populate core_style table
INSERT INTO core_style (name, panel_type_id, design_id, price, panels_across, panels_down, panel_overlap, designs_on_top, designs_on_bottom, created_at, updated_at) VALUES
    ('ATFO', (SELECT id FROM core_paneltype WHERE name = 'Frame Only'), (SELECT id FROM core_design WHERE name = 'Duncans'), 10.00, 1, 1, 0, TRUE, FALSE, datetime('now'), datetime('now')),
    ('CTFP', (SELECT id FROM core_paneltype WHERE name = 'Flat Panel'), (SELECT id FROM core_design WHERE name = 'Crown'), 10.00, 1, 1, 0.25, TRUE, TRUE, datetime('now'), datetime('now')),
    ('CTFP-2X2', (SELECT id FROM core_paneltype WHERE name = 'Flat Panel'), (SELECT id FROM core_design WHERE name = 'Crown'), 10.00, 2, 2, 0.25, TRUE, FALSE, datetime('now'), datetime('now')),
    ('CTRP-2X3', (SELECT id FROM core_paneltype WHERE name = 'Raised Panel'), (SELECT id FROM core_design WHERE name = 'Crown'), 14.00, 2, 3, 0.312, TRUE, TRUE, datetime('now'), datetime('now')),
    ('CTRP-5P', (SELECT id FROM core_paneltype WHERE name = 'Raised Panel'), (SELECT id FROM core_design WHERE name = 'Crown'), 14.00, 5, 1, 0.312, TRUE, FALSE, datetime('now'), datetime('now')),
    ('DFDF', (SELECT id FROM core_paneltype WHERE name = 'Drawer Front'), (SELECT id FROM core_design WHERE name = 'Square'), 3.50, 1, 1, 0, FALSE, FALSE, datetime('now'), datetime('now')),
    ('OTFP-DP', (SELECT id FROM core_paneltype WHERE name = 'Flat Panel'), (SELECT id FROM core_design WHERE name = 'Oval'), 10.00, 1, 2, 0.25, TRUE, TRUE, datetime('now'), datetime('now')),
    ('SHAKER-FP-4P', (SELECT id FROM core_paneltype WHERE name = 'Flat Panel'), (SELECT id FROM core_design WHERE name = 'Square'), 6.00, 4, 1, 0.25, FALSE, FALSE, datetime('now'), datetime('now')); 