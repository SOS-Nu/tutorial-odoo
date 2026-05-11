from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    """ 
    Model chính cho Đơn hàng. 
    Kế thừa từ mail.thread để sử dụng tính năng Chatter (Log lịch sử).
    """
    _name = 'sale.management.order'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Chuẩn Odoo Official
    _description = 'Sale Order Simulation'
    _order = 'date_order desc, id desc'

    # Các trường dữ liệu (Fields)
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    date_order = fields.Datetime(string='Order Date', required=True, readonly=False, index=True, default=fields.Datetime.now)
    
    # Quan hệ One2many: Một đơn hàng có nhiều dòng chi tiết
    order_line = fields.One2many('sale.management.order.line', 'order_id', string='Order Lines', copy=True)
    
    # Các trường tính toán (Computed Fields)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=True)
    total_quantity = fields.Float(string='Total Quantity', compute='_compute_total_quantity', store=True) # Trường mới
    
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    # Trạng thái đơn hàng (Workflow)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft', tracking=True)

    @api.depends('order_line.price_subtotal')
    def _amount_all(self):
        """ Hàm tính tổng tiền tự động khi có thay đổi ở các dòng chi tiết """
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.order_line)
            amount_tax = amount_untaxed * 0.1 # Giả định thuế VAT 10%
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('order_line.product_uom_qty')
    def _compute_total_quantity(self):
        """ 
        Sử dụng Python List Comprehension: Cách viết gọn đặc trưng của Python.
        Thay vì dùng vòng lặp for thông thường, ta có thể sum danh sách ngay lập tức.
        """
        for order in self:
            order.total_quantity = sum(order.order_line.mapped('product_uom_qty'))

    @api.model_create_multi
    def create(self, vals_list):
        """ 
        Ghi đè hàm tạo mới để tự động lấy số thứ tự (Sequence).
        vals_list: danh sách các từ điển dữ liệu từ giao diện gửi về.
        """
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                # Lấy số tiếp theo từ sequence đã định nghĩa trong XML
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.management.order') or _('New')
        return super(SaleOrder, self).create(vals_list)

    @api.constrains('order_line')
    def _check_order_line(self):
        """ Ràng buộc: Đơn hàng phải có ít nhất một dòng chi tiết (Giống SAP) """
        for order in self:
            if not order.order_line:
                raise ValidationError(_("Một đơn hàng chuẩn không thể không có sản phẩm nào! Vui lòng thêm ít nhất một dòng chi tiết."))

    def unlink(self):
        """ 
        Ràng buộc: Không cho phép xóa đơn hàng nếu trạng thái khác 'Nháp' hoặc 'Hủy'.
        Đây là bảo mật dữ liệu nghiệp vụ quan trọng.
        """
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise ValidationError(_("Bạn không thể xóa đơn hàng đã được xác nhận hoặc hoàn thành. Vui lòng chuyển về nháp hoặc hủy trước khi xóa."))
        return super(SaleOrder, self).unlink()

    # Các hàm xử lý chuyển trạng thái (Action buttons)
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_apply_bulk_discount(self):
        """ 
        Demo cách Python tương tác với các dòng con (Collection).
        Trong .NET bạn có thể dùng LINQ, còn Odoo dùng vòng lặp đơn giản.
        """
        for order in self:
            # Lặp qua các dòng con trong đơn hàng
            for line in order.order_line:
                # Nếu đơn giá trên 1000, áp dụng giảm giá 10%
                if line.price_unit > 1000:
                    line.discount = 10.0
                else:
                    line.discount = 5.0

    def api_export_data(self):
        """ 
        Enterprise Practice: Hàm chuyên biệt để export dữ liệu ra JSON.
        Giúp Controller mỏng hơn và tập trung logic tại Model.
        """
        self.ensure_one() # Đảm bảo chỉ chạy trên 1 bản ghi
        return {
            "OrderNumber": self.name,
            "CustomerName": self.partner_id.name,
            "TotalAmount": self.amount_total,
            "TotalQty": self.total_quantity,
            "Status": self.state,
            "Lines": [{
                "Product": line.product_id.name,
                "Qty": line.product_uom_qty,
                "Price": line.price_unit,
                "Subtotal": line.price_subtotal
            } for line in self.order_line]
        }
