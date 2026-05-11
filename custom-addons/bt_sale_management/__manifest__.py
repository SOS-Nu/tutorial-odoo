{
    'name': 'BT Sale Management Simulation',
    'version': '1.0',
    'summary': 'Mô phỏng quy trình Sale Order chuẩn doanh nghiệp',
    'description': """
        Module mô phỏng quy trình bán hàng.
    """,
    'author': 'Antigravity',
    'category': 'Sales/Sales',
    'summary': 'Mô phỏng quy trình Sale Order chuẩn doanh nghiệp',
    'description': """
        Module mô phỏng quy trình bán hàng theo phong cách Odoo Official.
    """,
    'depends': [
        'base', 
        'product', 
        'sale', 
        'mail' # Cần thiết cho tính năng Chatter (Tracking log)
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/sale_management_data.xml', # Load số thứ tự tự động
        'views/combined_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
