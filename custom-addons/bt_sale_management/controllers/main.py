import json
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

class SaleOrderController(http.Controller):

    # Enterprise Tip: Nên để các cấu hình này vào System Parameters trong Odoo
    KEYS = {
        "ADMIN_TOKEN_123": 2,
        "PORTAL_TOKEN_456": 4,
    }

    def _get_user(self):
        """ Xác thực và trả về user object """
        key = request.httprequest.headers.get('X-Api-Key')
        user_id = self.KEYS.get(key)
        return request.env['res.users'].sudo().browse(user_id) if user_id else None

    def _make_response(self, success, message, data=None, status=200, errors=None):
        """ Tạo JSON Response đồng nhất """
        result = {
            "Success": success,
            "Message": message,
            "Data": data or [],
            "Errors": errors
        }
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')],
            status=status
        )

    @http.route('/api/get_orders', type='http', auth='none', methods=['GET', 'POST'], csrf=False)
    def get_orders(self, **kwargs):
        user = self._get_user()
        if not user:
            return self._make_response(False, "Unauthorized", status=401)

        try:
            # Clean Code: Logic lấy data đã được đẩy xuống Model
            orders = request.env['sale.management.order'].with_user(user).search([])
            data = [order.api_export_data() for order in orders]
            
            _logger.info("API: User %s fetched %s orders", user.name, len(orders))
            return self._make_response(True, f"Fetch success for {user.name}", data=data)
        except AccessError as e:
            return self._make_response(False, "Permission Denied", errors=[{"Message": str(e)}], status=403)
        except Exception as e:
            _logger.error("API Error: %s", str(e))
            return self._make_response(False, "Internal Server Error", errors=[{"Message": str(e)}], status=500)

    @http.route('/api/create_order', type='http', auth='none', methods=['POST'], csrf=False)
    def create_order(self, **kwargs):
        user = self._get_user()
        if not user:
            return self._make_response(False, "Unauthorized", status=401)

        try:
            params = json.loads(request.httprequest.data)
            if not params.get('partner_id'):
                return self._make_response(False, "Missing partner_id", status=400)

            # Tạo bản ghi bằng quyền của User
            new_order = request.env['sale.management.order'].with_user(user).create({
                'partner_id': params.get('partner_id'),
            })
            
            return self._make_response(True, "Created", data=new_order.api_export_data())
        except AccessError as e:
            return self._make_response(False, "Permission Denied", errors=[{"Message": str(e)}], status=403)
        except Exception as e:
            return self._make_response(False, "Error", errors=[{"Message": str(e)}], status=500)
