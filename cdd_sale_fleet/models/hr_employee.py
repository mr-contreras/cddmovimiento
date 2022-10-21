# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    type_employee = fields.Selection(string='Tipo de Empleado', selection=[('gruero', 'Gruero'), ('support', 'Ayudante')])

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        _logger.warning('paso _action_confirm1111111111111111111111111111111111111')
        args = [('name', operator, name)] + args
        if self._context.get('employee_sale'):
            task = self.env['project.task'].browse(self._context.get('employee_sale')) 
            employee_ids_in = []
            
            for rec in task.user_ids:
                if rec.employee_id.id not in employee_ids_in:
                    employee_ids_in.append(rec.employee_id.id)

            args = [('name', operator, name), ('id', 'in', employee_ids_in)] + args
            _logger.warning('paso _action_confirm@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', task, employee_ids_in)
#             print(nameError111)
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        else:
#             print(nameError222)
            return super(HrEmployee, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

