# -*- coding: utf-8 -*-
{
    'name': "wsem_cloud_crm",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Semantic Web Software SL",
    'website': "https://wsemantic.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'], 

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner.xml',
        'views/templates.xml',
       
    ],
    "assets":{       
        'web.assets_frontend':[
            'cloud_crm/static/src/js/signup_step1.js',
            'cloud_crm/static/src/css/factuo.css',
        ], 
    }, 
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "license": "AGPL-3",
}
