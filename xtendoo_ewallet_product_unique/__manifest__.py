{
    'name': 'Xtendoo EWallet Product Unique',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Añade relación entre programa de lealtad y producto único para monedero electrónico',
    'description': """
        Este módulo extiende el modelo loyalty.program para añadir una relación
        con un producto específico que será el único que se puede pagar con el
        monedero electrónico (ewallet). Incluye validaciones y filtrado de
        monederos activos en el punto de venta.
    """,
    'author': 'Xtendoo',
    'website': 'https://www.xtendoo.es',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'loyalty',
        'product',
        'sale',
        'point_of_sale',
    ],
    'data': [
        'views/loyalty_program_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
