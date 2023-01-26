from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    start_hourmeter = fields.Float(string='Ultimo Horometro',help='Hourmeter measure of the vehicle at the moment of this log')
    start_hourmeter_unit = fields.Selection([
        ('hours', 'hrs'),
        ('minutes', 'min')
        ], 'hourmeter Unit', default='hours', help='Unit of the hourmeter ', required=True)

    hourmeter_count = fields.Integer(compute="_compute_count_hourmeter", string='Hourmeter')
    
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