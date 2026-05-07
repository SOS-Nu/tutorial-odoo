from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_note = fields.Text()

    def action_confirm(self):

        self.customer_note = "Confirmed"

        return super().action_confirm()