from django.apps import apps
from qscm.settings import BASE_DIR


app = apps.get_app_config('horizon')


datasheet_fields_set = [
    ('Serial', None),
    ('Location', app.get_model('Location')),
    ('Date', app.get_model('DataDate')),
    ('Quantity', app.get_model('Quantity')),
    ('Vendor', app.get_model('Company')),
]


option_list = {
    'yesno': ('Yes', 'No'),
    'yesnona': ('Yes', 'No', 'N/A'),
    'truefalse': ('True', 'False'),
    'truefalsena': ('True', 'False', 'N/A'),
    'minmax': ('Minimum', 'Maximum'),
    'minmaxna': ('Minimum', 'Maximum', 'N/A'),
}


save_folders = {
    'datasheet_template': BASE_DIR + '/horizon/xl_templates/',
    'datasheet_file': BASE_DIR + '/horizon/xl_datasheets/',
}


quantity_roles = [
    ('base', 'Base'),
    ('conv', 'Convertible'),
    ('freq', 'Frequency'),
    ('sapc', 'Price Condition'),
    ('mres', 'Multiple Restrictions'),
    ('chgu', 'Chargeable')
]
