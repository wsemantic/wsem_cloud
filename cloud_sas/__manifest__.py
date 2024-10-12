{
    'name': "cloud_sas",
    'version': '1.0',
    'category': 'API',
    'depends': ['base', 'web'],
    'data': [],
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
        'data/user_external_id.xml',
        'security/groups.xml',
        'security/ir_rule.xml',
        'views/hide_admin.xml',
    ],
}
