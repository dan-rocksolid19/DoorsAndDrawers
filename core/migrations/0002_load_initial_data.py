from django.db import migrations

def load_initial_data(apps, schema_editor):
    # Get models
    Design = apps.get_model('core', 'Design')
    EdgeProfile = apps.get_model('core', 'EdgeProfile')
    PanelRise = apps.get_model('core', 'PanelRise')
    PanelType = apps.get_model('core', 'PanelType')
    WoodStock = apps.get_model('core', 'WoodStock')
    Style = apps.get_model('core', 'Style')

    # Load designs
    designs = [
        {'name': 'Crown', 'arch': True},
        {'name': 'Duncans', 'arch': True},
        {'name': 'French', 'arch': True},
        {'name': 'Heritage', 'arch': True},
        {'name': 'Oval', 'arch': True},
        {'name': 'Provincial', 'arch': True},
        {'name': 'Square', 'arch': False},
    ]
    for design in designs:
        Design.objects.create(**design)

    # Load edge profiles
    edge_profiles = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6']
    for profile in edge_profiles:
        EdgeProfile.objects.create(name=profile)

    # Load panel rises
    panel_rises = ['PanelRaise1', 'PanelRaise2', 'PanelRaise3']
    for rise in panel_rises:
        PanelRise.objects.create(name=rise)

    # Load panel types
    panel_types = [
        {
            'name': 'Drawer Front',
            'surcharge_width': 28,
            'surcharge_height': 10,
            'surcharge_percent': 15,
            'minimum_sq_ft': 0.8,
            'use_flat_panel_price': False
        },
        {
            'name': 'Flat Panel',
            'surcharge_width': 22,
            'surcharge_height': 39,
            'surcharge_percent': 15,
            'minimum_sq_ft': 2,
            'use_flat_panel_price': True
        },
        {
            'name': 'Frame Only',
            'surcharge_width': 22,
            'surcharge_height': 39,
            'surcharge_percent': 15,
            'minimum_sq_ft': 2,
            'use_flat_panel_price': True
        },
        {
            'name': 'Raised Panel',
            'surcharge_width': 22,
            'surcharge_height': 39,
            'surcharge_percent': 15,
            'minimum_sq_ft': 2,
            'use_flat_panel_price': False
        },
        {
            'name': 'Slab',
            'surcharge_width': 22,
            'surcharge_height': 39,
            'surcharge_percent': 15,
            'minimum_sq_ft': 2,
            'use_flat_panel_price': True
        }
    ]
    for panel_type in panel_types:
        PanelType.objects.create(**panel_type)

    # Load wood stock
    wood_stock = [
        {'name': 'Alder', 'raised_panel_price': 7.50, 'flat_panel_price': 7.00},
        {'name': 'Ash', 'raised_panel_price': 5.00, 'flat_panel_price': 4.50},
        {'name': 'Basswood', 'raised_panel_price': 5.00, 'flat_panel_price': 4.50},
        {'name': 'Birch', 'raised_panel_price': 6.50, 'flat_panel_price': 6.00},
        {'name': 'Cherry', 'raised_panel_price': 8.50, 'flat_panel_price': 8.00},
        {'name': 'Cypress', 'raised_panel_price': 8.50, 'flat_panel_price': 8.00},
        {'name': 'Hickory', 'raised_panel_price': 6.50, 'flat_panel_price': 6.00},
        {'name': 'Mahogany', 'raised_panel_price': 9.50, 'flat_panel_price': 9.00},
        {'name': 'Red Oak', 'raised_panel_price': 5.00, 'flat_panel_price': 4.50},
    ]
    for wood in wood_stock:
        WoodStock.objects.create(**wood)

    # Load styles
    styles = [
        {
            'name': 'ATFO',
            'panel_type': PanelType.objects.get(name='Frame Only'),
            'design': Design.objects.get(name='Duncans'),
            'price': 10.00,
            'panels_across': 1,
            'panels_down': 1,
            'panel_overlap': 0,
            'designs_on_top': True,
            'designs_on_bottom': False
        },
        {
            'name': 'CTFP',
            'panel_type': PanelType.objects.get(name='Flat Panel'),
            'design': Design.objects.get(name='Crown'),
            'price': 10.00,
            'panels_across': 1,
            'panels_down': 1,
            'panel_overlap': 0.25,
            'designs_on_top': True,
            'designs_on_bottom': True
        },
        {
            'name': 'CTFP-2X2',
            'panel_type': PanelType.objects.get(name='Flat Panel'),
            'design': Design.objects.get(name='Crown'),
            'price': 10.00,
            'panels_across': 2,
            'panels_down': 2,
            'panel_overlap': 0.25,
            'designs_on_top': True,
            'designs_on_bottom': False
        },
        {
            'name': 'CTRP-2X3',
            'panel_type': PanelType.objects.get(name='Raised Panel'),
            'design': Design.objects.get(name='Crown'),
            'price': 14.00,
            'panels_across': 2,
            'panels_down': 3,
            'panel_overlap': 0.312,
            'designs_on_top': True,
            'designs_on_bottom': True
        },
        {
            'name': 'CTRP-5P',
            'panel_type': PanelType.objects.get(name='Raised Panel'),
            'design': Design.objects.get(name='Crown'),
            'price': 14.00,
            'panels_across': 5,
            'panels_down': 1,
            'panel_overlap': 0.312,
            'designs_on_top': True,
            'designs_on_bottom': False
        },
        {
            'name': 'DFDF',
            'panel_type': PanelType.objects.get(name='Drawer Front'),
            'design': Design.objects.get(name='Square'),
            'price': 3.50,
            'panels_across': 1,
            'panels_down': 1,
            'panel_overlap': 0,
            'designs_on_top': False,
            'designs_on_bottom': False
        },
        {
            'name': 'OTFP-DP',
            'panel_type': PanelType.objects.get(name='Flat Panel'),
            'design': Design.objects.get(name='Oval'),
            'price': 10.00,
            'panels_across': 1,
            'panels_down': 2,
            'panel_overlap': 0.25,
            'designs_on_top': True,
            'designs_on_bottom': True
        },
        {
            'name': 'SHAKER-FP-4P',
            'panel_type': PanelType.objects.get(name='Flat Panel'),
            'design': Design.objects.get(name='Square'),
            'price': 6.00,
            'panels_across': 4,
            'panels_down': 1,
            'panel_overlap': 0.25,
            'designs_on_top': False,
            'designs_on_bottom': False
        }
    ]
    for style in styles:
        Style.objects.create(**style)

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ] 