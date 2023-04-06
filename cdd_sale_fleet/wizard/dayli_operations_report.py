from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class AdvancesNotAppliedWizard(models.TransientModel):
    _name = 'dayli.operations.report.wizard'

    start_date = fields.Date(string="Start Date", required = True)
    end_date = fields.Date(string="End Date", required = True)
    
    def action_print_report(self):
        vals = {
            'start_date': self.start_date,
            'end_date': self.end_date, 
        }
        data = vals

        obj =  self.env['project.task'].browse(self._context.get('active_id'))
#         raise ValidationError('Solo puede eliminar registros en estado inactivo. %s' %(obj))
        obj.sudo().write({
            'start_date_w': self.start_date,
            'end_date_w': self.end_date ,
        })
        return self.env.ref('cdd_sale_fleet.cdd_action_report_sale_task').report_action(obj)

    @api.constrains('start_date','end_date')
    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_('The initial date can not be greater than the final.'))
                
                
class AdvancesNotAppliedWizard(models.TransientModel):
    _name = 'operations.report.wizard'
    
    type_filtered = fields.Selection([
        ('date_create', 'Fecha de creacion'),
        ('date_ejec', 'Fecha de ejecucion'),
        ('uni_eco', 'Unidad ecónomica'),
        ('state', 'Etapa'),
        ('all', 'Todos'),
    ], string='Tipo de filtro', required = True, default ='all')
    
    
#     state = fields.Selection([
#         ('draft', 'Cotizacion'),
#         ('sent', 'Cotizacion enviada'),
#         ('sale ', 'Orden de venta'),
#         ('done', 'Bloqueado'),
#         ('cancel', 'Cancelado'),
#     ], string='Tipo de filtro', required = True)
    
#     vehicle_id = fields.Many2one('fleet.vehicle', string='Unidad ecónomica')
    
    date_filtered_init = fields.Date('Desde')
    date_filtered_end = fields.Date('Hasta')
    
    
    def action_print_report(self):
#         obj =  self.env['project.task'].browse(self._context.get('active_id'))
#         raise ValidationError('Solo puede eliminar registros en estado inactivo. %s' %(obj))
        
        objs = self.env['sale.order'].search([
            ('id', '>', 0)
        ])
#         raise ValidationError('Solo puede eliminar registros en estado inactivo. %s' %(objs))
        
        return objs.env.ref('cdd_sale_fleet.cdd_action_report_sale_task_2').report_action(objs)
    

    def action_print_report_xlsx(self):
        objs = self.env['sale.order'].search([
            ('id', '>', 0)
        ])
        
        return self.sudo().env.ref('cdd_sale_fleet.cdd_action_report_sale_task_2_xlsx').report_action(self)
