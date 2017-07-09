from django.apps import apps


app = apps.get_app_config('horizon')


datasheet_fields = [
    ('Serial', None),
    ('Category', app.get_model('Category')),
    ('Location', app.get_model('Geo')),
    ('Date', app.get_model('DataDate')),
    ('Quantity', app.get_model('Quantity')),
    ('Vendor', app.get_model('Company')),
]
