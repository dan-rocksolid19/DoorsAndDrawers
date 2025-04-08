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