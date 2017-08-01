from django.apps import apps
from qscm.settings import BASE_DIR


app = apps.get_app_config('horizon')


datasheet_fields_set = [
    ('Serial', None),
    ('Category', app.get_model('Category')),
    ('Location', app.get_model('Location')),
    ('Date', app.get_model('DataDate')),
    ('Quantity', app.get_model('Quantity')),
    ('Vendor', app.get_model('Company')),
]


option_list = {
    'binary': ('Yes', 'No'),
}


template_save_folders = {
    'datasheet_template': BASE_DIR + '/horizon/xl_templates/'
}


quantity_types = [
    ('base', 'Base'),
    ('conv', 'Convertible'),
    ('sapc', 'Price Condition'),
    ('mres', 'Multiple Restrictions'),
    ('freq', 'Frequency')
]
