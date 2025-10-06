{
    'name': "cloud_sas",
    'version': '18.0.0.0',
    'category': 'API',
    'depends': ['base', 'web', 'account', 'mail'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'summary': "Facuoo clientes",
    'description': "Facuoo clientes",
    'author': "Semantic Web Software SL",
    'website': "https://wsemantic.com",
    'license': "AGPL-3",
    
    'data': [
        # 'security/ir.model.access.csv',
        'security/groups.xml',
        'security/ir_rules.xml',
        'data/user_external_id.xml',
        'data/hide_record_rules_menu.xml',
        'data/hide_record_rules_menu.xml',        
        'views/views.xml',

    ],
    "assets":{       
        'web.assets_backend':[
            'cloud_sas/static/src/js/user_menu_item.js',
        ],
    }, 
}
