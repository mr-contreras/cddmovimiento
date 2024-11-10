# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, date
import logging
import pytz

_logger = logging.getLogger(__name__)

class projectTask(models.Model):
    _inherit = 'project.task'

    #     planned_hours_compute = fields.Float("Horas planeadas 2", help='Time planned to achieve this task (including its sub-tasks).', tracking=True, compute = 'get_planned_hours_compute')

    start_date_w = fields.Date(string="Fecha inicio")
    end_date_w = fields.Date(string="Fecha fin")
    folio_w = fields.Char(string="Folio")

    def reset_binnacle_ids(self):
        #         return
        self.end_date_w = False
        self.start_date_w = False

    def get_binnacle_ids(self):
        user_tz = self.env.user.tz or pytz.utc
        filtrado_fecha = []
        filtrado = []
        
        filtrado_fecha = self.binnacle_ids.filtered(lambda l: self.start_date_w <= (l.date_init.astimezone(pytz.timezone(user_tz))).date() <= self.end_date_w)
        
        if self.folio_w:
            filtrado = filtrado_fecha.filtered(lambda l: self.folio_w == l.folio)
            if filtrado is not None:
                return filtrado
            else:
                raise ValidationError(_('No se encontró información para estos parámetros'))
        else:
            return filtrado_fecha

    def action_report_domain(self):
        return {
            'name': 'Reporte diario',
            'type': 'ir.actions.act_window',
            'res_model': 'dayli.operations.report.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    # @api.model
    # def default_get(self, fields):
    #   res = super(projectTask, self).default_get(fields)

    # context = dict(self.env.context)
    #   context.update({'current_model':self , 'active_id':self.id})
    #  self.env.context = context

    # raise ValidationError(self._context)
    # return res
