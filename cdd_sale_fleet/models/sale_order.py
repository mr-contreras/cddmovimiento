from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    model_fleet_id = fields.Many2one(comodel_name='fleet.vehicle.model', string='Modelo de la grúa')
    nombre_pozo = fields.Char("Nombre Pozo", required=True)

    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if self.tasks_ids:
            total_hours = 0
            for line in self.order_line:
                total_hours += line.product_uom_qty

            self.tasks_ids[0].planned_hours = total_hours
        return result
    
    def action_report_domain_2(self):
        return {
            'name': 'Reporte diario',
            'type': 'ir.actions.act_window',
            'res_model': 'operations.report.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    def get_names_users_assigned(self):
        str_grueros = ''
        if self.tasks_ids:
            grueros_array = self.tasks_ids[0].user_ids.mapped('name')
            for i in grueros_array: str_grueros+= (i + ' , ')
        return str_grueros
    
    def get_status_invoice_paid(self, status):
        payment_state = 'Sin Facturar'
        if self.invoice_ids:
            if status == 'not_paid':
                payment_state = 'Sin pagar'
            elif status == 'in_payment':
                payment_state = 'En Proceso de Pago'
            elif status == 'paid':
                payment_state = 'Pagado'
            elif status == 'partial':
                payment_state = 'Pagado Parcialmente'
            elif status == 'reversed':
                payment_state = 'Revertido'
            elif status == 'invoicing_legacy':
                payment_state = 'Sistema anterior de facturacion' 
        return payment_state
#     @api.onchange('order_line')
#     def recompute_hours_task(self):
#         total_hours = 0
#         for line in self.order_line    


#     def _action_confirm(self):
# #         _logger.warning('paso _action_confirm@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
# #         print(errorConfirm)
#         result = super()._action_confirm()
#         if len(self.company_id) == 1:
#             # All orders are in the same company
#             self.order_line.sudo().with_company(self.company_id)._timesheet_service_generation()
#         else:
#             # Orders from different companies are confirmed together

#             for order in self:
#                 order.order_line.sudo().with_company(order.company_id)._timesheet_service_generation()
#         return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Documentacion del metodo
    # https://github.com/odoo/odoo/blob/909b9b46104e9d3182f7c461c611bf6491b5d181/addons/sale_project/models/sale_order.py#L208

    def _timesheet_create_task_prepare_values(self, project):
        self.ensure_one()
        planned_hours = self._convert_qty_company_hours(self.company_id)
        sale_line_name_parts = self.name.split('\n')
        title = sale_line_name_parts[0] or self.product_id.name
        description = '<br/>'.join(sale_line_name_parts[1:])
        return {
            # 'name': title if project.sale_line_id else '%s: %s' % (self.order_id.name or '', title),
            'name': '%s : %s' % (self.order_id.name, self.order_id.nombre_pozo),
            'planned_hours': planned_hours,
            'partner_id': self.order_id.partner_id.id,
            'email_from': self.order_id.partner_id.email,
            'description': description,
            'project_id': project.id,
            'sale_line_id': self.id,
            'sale_order_id': self.order_id.id,
            'company_id': project.company_id.id,
            'user_ids': False,
            'model_fleet_id': self.order_id.model_fleet_id.id,
            'sale_line_id': False,
        }

    #     def _timesheet_service_generation(self):
    #         print(op)

    #   @override
    def _timesheet_create_task(self, project):

        if self.order_id.tasks_ids:
            #             print(errorTaskIf)
            return self.order_id.tasks_ids[0]
        else:
            task = self.env['project.task'].sudo().search([
                ('sale_order_id', '=', self.order_id.id)
            ])
            if not task:
                values = self._timesheet_create_task_prepare_values(project)
                task = self.env['project.task'].sudo().create(values)
                self.write({'task_id': task.id})
                # post message on task
                task_msg = _(
                    "This task has been created from: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a> (%s)") % (
                               self.order_id.id, self.order_id.name, self.product_id.name)
                task.message_post(body=task_msg)
                #             print(errorTaskElse)
                return task

    #   @override
    def _timesheet_create_project(self):
        self.ensure_one()

        if self.order_id.project_ids:
            return self.order_id.project_ids[0]
        else:
            project = self.env['project.project'].sudo().search([
                ('sale_order_id', '=', self.order_id.id)
            ])
            if not project:
                values = self._timesheet_create_project_prepare_values()
                if self.product_id.project_template_id:
                    values['name'] = "%s - %s" % (values['name'], self.product_id.project_template_id.name)
                    project = self.product_id.project_template_id.copy(values)
                    project.tasks.write({
                        'sale_line_id': self.id,
                        'partner_id': self.order_id.partner_id.id,
                        'email_from': self.order_id.partner_id.email,
                    })
                    # duplicating a project doesn't set the SO on sub-tasks
                    project.tasks.filtered(lambda task: task.parent_id != False).write({
                        'sale_line_id': self.id,
                        'sale_order_id': self.order_id,
                    })
                else:
                    project = self.env['project.project'].create(values)

                # Avoid new tasks to go to 'Undefined Stage'
                if not project.type_ids:
                    project.type_ids = self.env['project.task.type'].create({'name': _('New')})

                # link project as generated by current so line
                self.write({'project_id': project.id})
                return project
