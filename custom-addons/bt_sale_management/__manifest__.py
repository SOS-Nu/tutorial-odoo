{
    'name': 'BT Sale Management Simulation',
    'version': '1.0',
    'summary': 'Mô phỏng quy trình Sale Order chuẩn doanh nghiệp',
    'description': """
        Module mô phỏng quy trình bán hàng.
    """,
    'author': 'Antigravity',
    'category': 'Sales',
    'depends': ['base', 'product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/combined_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
