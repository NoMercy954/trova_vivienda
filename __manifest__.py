{
    'name': 'Trova_Vivienda',
    'version': '1.0',
    'summary': 'Personalizacion de Trova',
    'description': 'Formulario viviendas',
    'category': 'Personalizacion',
    'author': 'William Colin Macedo',
    'website': 'www.xmarts.com',
    'depends': ['base', 'contacts','hr','sale'],
    'data': ['views/view.xml',
             'views/view_saneam.xml',
             'views/view_tit.xml',
             'views/view_paquete.xml',
             'reports/contrato_venta.xml' ],

    'installable': True,
    'aplication': True,
    'auto_install': False,
}