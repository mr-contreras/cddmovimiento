# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains('order_line')
    def check_constraint_quantity(self):
        for record in self:
            if record.order_line:
                for line in record.order_line:
                    minimum_order_qty = line.product_id.minimum_quantity
                    if line.product_uom_qty != minimum_order_qty:
                        raise ValidationError(_('Este producto/servicio ' + line.name + ' solamente puede venderse en ' + str(minimum_order_qty) + ' unidades.'))
