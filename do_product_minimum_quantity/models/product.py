# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    minimum_quantity = fields.Float(string='Minimum Quantity', help="This field display minimum order qunatity", default=1.0)
