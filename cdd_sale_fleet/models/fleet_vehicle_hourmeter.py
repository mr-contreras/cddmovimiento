from odoo import api, fields, models
import logging
# from openerp.osv import orm
import logging
_logger = logging.getLogger(__name__)


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    
    horometro_control_4000 = fields.Float(string='Horometro 4000')
    horometro_control_1600 = fields.Float(string='Horometro 1600')
    
    total_hourmeter = fields.Float(string='Total Horometro', compute = 'get_totals_hourmeter')
    ultimate_service = fields.Float(string='Ultimo servicio(Horometro)')
    start_hourmeter = fields.Float(string='Ultimo Horometro',help='Hourmeter measure of the vehicle at the moment of this log' , compute = 'get_totals_hourmeter')
    start_hourmeter_unit = fields.Selection([
        ('hours', 'hrs'),
        ('minutes', 'min')
        ], 'hourmeter Unit', default='hours', help='Unit of the hourmeter ', required=True)
    
    
    send_email = fields.Char('Enviar a')
    
    hourmeter_count = fields.Integer(compute="_compute_count_hourmeter", string='Hourmeter')
    fleet_services_config_id = fields.Many2one(comodel_name='fleet.services.config', string='')
    
    
    def get_totals_hourmeter(self):
        for rec in self:
            rec.total_hourmeter = 0
            rec.start_hourmeter = 0
            total_hourmeter = 0 
            hourmeter = rec.env['fleet.vehicle.hourmeter'].search([
                ('vehicle_id', '=', rec.id)
            ]) 
            
            for h in hourmeter:
                total_hourmeter += h.value
            
            rec.total_hourmeter = total_hourmeter
            rec.start_hourmeter = hourmeter[0].value if hourmeter else False
    
    def _compute_count_hourmeter(self):
        hourmeter = self.env['fleet.vehicle.hourmeter']
        for record in self:
            record.hourmeter_count = hourmeter.search_count([('vehicle_id', '=', record.id)])

    def return_action_to_open_hourmeter(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('cdd_sale_fleet.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
            )
            return res
        return False

    def return_action_to_open_notifications(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('cdd_sale_fleet.action_fleet_maintenance_notifications_act_window')
        res.update(
            context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
            domain=[('vehicle_id', '=', self.id)]
        )
        return res
    
    
    
    def ir_cron_service_seven_days(self):
        
        vehicles = self.env['fleet.vehicle'].search([
            ('id','>',0)
        ])
        
        
        for v in vehicles:
            services_type = self.env['fleet.service.type'].search([
                ('name','=','Factura de proveedor'),
            ], limit = 1)

            services_config = self.env['fleet.services.config'].search([
                ('quantity','=',7),
                ('type_range','=','days'),
            ])

            self.env['fleet.vehicle.log.services'].create({
                'service_type_id':services_type.id if services_type else False,
                'vehicle_id':v.id,
                'type_service_id':services_config.id if services_config else False,
            })
            
            
    def ir_cron_service_one_days(self):
        
        vehicles = self.env['fleet.vehicle'].search([
            ('id','>',0)
        ])
        
        
        for v in vehicles:
            services_type = self.env['fleet.service.type'].search([
                ('name','=','Factura de proveedor'),
            ], limit = 1)

            services_config = self.env['fleet.services.config'].search([
                ('quantity','=',1),
                ('type_range','=','days'),
            ])

            self.env['fleet.vehicle.log.services'].create({
                'service_type_id':services_type.id if services_type else False,
                'vehicle_id':v.id,
                'type_service_id':services_config.id if services_config else False,
            })
           

        
    
    
    
    def _services_vehicle(self):
        vehicles = self.env['fleet.vehicle'].search([
            ('id','>',0)
        ])
        
        for v in vehicles:
            dff = v.total_hourmeter - v.ultimate_service
            if dff > 400:
                v.ultimate_service = v.total_hourmeter
                
                # create service 400 ============================================
                services_type = self.env['fleet.service.type'].search([
                    ('name','=','Factura de proveedor'),
                ], limit = 1)
                
                services_config = self.env['fleet.services.config'].search([
                    ('quantity','=',400),
                    ('type_range','=','hours'),
                ])
                
                self.env['fleet.vehicle.log.services'].create({
                    'service_type_id':services_type.id if services_type else False,
                    'vehicle_id':v.id,
                    'type_service_id':services_config.id if services_config else False,
                })
                v.horometro_control_1600 += dff
                v.horometro_control_4000 += dff
                # create service 400 ============================================
                
                
                # if v.horometro_control += 400:
                #     pass
                    
                if  v.horometro_control_1600 > 1600:
                    # create service 1600
                    services_config = self.env['fleet.services.config'].search([
                        ('quantity','=',1600),
                        ('type_range','=','hours'),
                    ], limit = 1)

                    self.env['fleet.vehicle.log.services'].create({
                        'service_type_id':services_type.id if services_type else False,
                        'vehicle_id':v.id,
                        'type_service_id':services_config.id if services_config else False,
                    })
                    v.horometro_control_1600 = 0
                    
                
                if  v.horometro_control_4000 > 4000:
                    # create service 4000
                    services_config = self.env['fleet.services.config'].search([
                        ('quantity','=',4000),
                        ('type_range','=','hours'),
                    ], limit = 1)

                    self.env['fleet.vehicle.log.services'].create({
                        'service_type_id':services_type.id if services_type else False,
                        'vehicle_id':v.id,
                        'type_service_id':services_config.id if services_config else False,
                    })
                    v.horometro_control_4000 = 0
            
            
            # elif (400 -dff) <=  v.aviso:
            #     # notificacion servicio proximo :
            #     mail_template = self.env.ref ('cdd_sale_fleet.fleet_maintenance_notification',self.id)
            #     mail_template.send_mail(self.id, force_send = True)
        pass
        
    
    
        
        
        
        
            
class FleetVehicleHourmeter(models.Model):
    _name = 'fleet.vehicle.hourmeter'
    _description = 'Hourmeter log for a vehicle'
    _order = 'date desc'

    name = fields.Char(compute='_compute_vehicle_log_name', store=True)
    date = fields.Date(default=fields.Date.context_today)
    value = fields.Float('Hourmeter Value', group_operator="max")
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True)
    unit = fields.Selection(related='vehicle_id.start_hourmeter_unit', string="Unit", readonly=True)
    driver_id = fields.Many2one(related="vehicle_id.driver_id", string="Driver", readonly=False)

    @api.depends('vehicle_id', 'date')
    def _compute_vehicle_log_name(self):
        for record in self:
            name = record.vehicle_id.name
            if not name:
                name = str(record.date)
            elif record.date:
                name += ' / ' + str(record.date)
            record.name = name

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.unit = self.vehicle_id.start_hourmeter_unit