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
    'version': '18.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale','l10n_es_toponyms', 'contract', 'website'], 

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/partner.xml',
        'views/templates.xml',
        'views/sign_up_step1.xml',
        'views/sign_up_step2.xml',
        'views/signup_error.xml',
        'views/success_register.xml',
        'views/owl_step1_template.xml',
        'views/contract_bank.xml',
        'views/contract_portal_img.xml',
    ],
    "assets":{       
        'web.assets_frontend':[
            'cloud_crm/static/src/js/signup_step1.js',
            'cloud_crm/static/src/js/signup_step2.js',
            'cloud_crm/static/src/css/factuo.css',
            'cloud_crm/static/src/lib/select2/select2.css',
            'cloud_crm/static/src/lib/select2/select2.js',
            'cloud_crm/static/src/lib/select2-bootstrap-css/select2-bootstrap.css',
        ], 
        # 'web.assets_backend':[
        #     'cloud_crm/static/src/js/user_menu_item.js',
        # ],
    }, 
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "license": "AGPL-3",
}
