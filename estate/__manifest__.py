{
    'name':'Real Estate',
    'depends':['base'],
    'data':[
        'data/estate.property.type.csv',
        'security/ir.model.access.csv',
        'views/estate_property_offer_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/res_users_view.xml',
        'views/estate_menus.xml',
    ],
    'demo':[
        'demo/estate_property.xml',
        'demo/estate_property_offer_demo.xml',
    ],
    'application': True
}
