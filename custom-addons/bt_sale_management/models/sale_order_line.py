from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _name = 'sale.management.order.line'
    _description = 'Sale Order Line Simulation'

    order_id = fields.Many2one('sale.management.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    discount = fields.Float(string='Discount (%)', default=0.0) # Trường mới
    
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency', readonly=True)

    @api.depends('product_uom_qty', 'price_unit', 'discount')
    def _compute_amount(self):
        """ 
        Logic: Thành tiền = (Số lượng * Đơn giá) * (1 - % Chiết khấu)
        Đây là cách Python xử lý tính toán số học cơ bản.
        """
        for line in self:
            price = line.product_uom_qty * line.price_unit
            discount_amount = price * (line.discount / 100.0)
            line.price_subtotal = price - discount_amount

    @api.onchange('product_uom_qty', 'discount')
    def _onchange_quantity_validation(self):
        """ Giống như Validation Logic trong C# """
        if self.product_uom_qty < 0:
            return {
                'warning': {
                    'title': "Cảnh báo số lượng",
                    'message': "Số lượng không được nhỏ hơn 0. Hệ thống đã tự động reset về 1.",
                }
            }
            self.product_uom_qty = 1.0

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        self.price_unit = self.product_id.list_price
