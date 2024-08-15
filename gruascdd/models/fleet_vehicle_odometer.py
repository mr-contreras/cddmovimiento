# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetVehicleOdometer(models.Model):
    _inherit = "fleet.vehicle.odometer"

    binnacle_id = fields.Integer(string='Bitacora',store=True, readonly=True)
    task_name = fields.Char("Servicio", store=True, readonly=True)
    folio = fields.Char("Folio", store=True, readonly=True)
