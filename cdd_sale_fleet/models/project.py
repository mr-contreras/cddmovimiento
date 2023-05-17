# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, date
import logging
import pytz

_logger = logging.getLogger(__name__)

class productProduct(models.Model):
    _inherit = 'product.product'

    in_sale_order = fields.Integer('in_sale_order', compute="_compute_in_sale_order", search="_search_in_sale_order")

    @api.depends('name')
    def _compute_in_sale_order(self):
        self.in_sale_order=1

    @api.model
    def _search_in_sale_order(self, operator, value):
        if operator == "=":
            task = self.env['project.task'].search([("id", "=", value)])
            order = self.env['sale.order'].search([("id", "=", task.sale_order_id.id)])
            if order:
                products = []
                for line in order.order_line:
                    if line.product_id.id not in products:
                        products.append(line.product_id.id)
                return [("id", "in", products)]
            else:
                return False
        else:
            return False

#    @api.model
#    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
#        args = args or []
#        #         raise ValidationError('%s , contexto ==> %s'%(self._context.get('name_product_sale'), self._context))
#        _logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@usando mi _name_search")
#        args = [('name', operator, name)] + args
#        if self._context.get('name_product_sale'):
#            _logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ eiste name_product_sale")
#           task = self.env['project.task'].browse(self._context.get('name_product_sale'))
#           array_product = []

#            filter_product = (p for p in task.sale_order_id.order_line)
#            for rec in filter_product:
#                if rec.product_id.id not in array_product:
#                    array_product.append(rec.product_id.id)

#            args = [('name', operator, name), ('id', 'in', array_product)] + args
#            _logger.info('paso _action_confirm@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', task, array_product)
            #             print(nameError111)
#            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
#        else:
            #             print(nameError222)
#            return super(productProduct, self)._name_search(name=name, args=args, operator=operator, limit=limit,
#                                                            name_get_uid=name_get_uid)


class projectBinacle(models.Model):
    _name = 'project.binacle'

    parent_id = fields.Many2one('project.task', string='Proyecto', required=True, ondelete='cascade', index=True,
                                copy=False, auto_join=True, )
    parent_id_int = fields.Integer(' ')
    product_id = fields.Many2one('product.product', string='Producto', required=True, ondelete='cascade', index=True,
                                 copy=False, domain=[('in_sale_order', '=', parent_id_int)])
    description = fields.Char('Descripción', related='product_id.name')
    date_init = fields.Datetime('Fecha hora inicio')
    date_end = fields.Datetime('Fecha hora final')
    delta = fields.Float(string='Delta', compute='_compute_delta', store=True)
    gruero_id = fields.Many2one('hr.employee', string='Gruero')
    support_id = fields.Many2one('hr.employee', string='Ayudante')
    comment = fields.Char('Comentario')
    pre_parent_id = fields.Many2one('project.task', string='pre_parent')
    odometer = fields.Integer('Odometro')
    hourmeter = fields.Integer('Horometro')

    available_product_ids = fields.Many2many('product.product', compute='_compute_available_product_ids')

    @api.depends('available_product_ids', 'product_id')
    def _compute_available_product_ids(self):
        for rec in self:
            order_id = rec.env['sale.order'].browse(rec._context.get('active_id'))
            if not order_id:
                task = rec.env['project.task'].browse(rec._context.get('default_parent_id_int'))
                _logger.warning('****************** TAKSK ******************')
                _logger.warning('****************** TAKSK ******************')
                _logger.warning(task)
                _logger.warning(task.project_sale_order_id)
                _logger.warning('****************** TAKSK ******************')
                _logger.warning('****************** TAKSK ******************')

                order_id = rec.env['sale.order'].search([('tasks_ids', 'in', task.id)], limit=1)
            res = order_id.order_line.mapped('product_id')
            # raise ValidationError('res -- ---------------- %s ----- %s ---->>'%(res, rec._context))1
            _logger.warning('productos disponibles -------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            _logger.warning('productos disponibles -------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            _logger.warning('productos disponibles -------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            _logger.warning('productos disponibles -------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            _logger.warning('productos disponibles -----2333--------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            _logger.warning(res)
            _logger.warning(rec._context)
            _logger.warning('productos33333 disponibles -------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            _logger.warning('productos disponibles -------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            _logger.warning('productos disponibles -------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            _logger.warning('productos disponibles -------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            # print(op)
            rec.available_product_ids = res

    @api.depends('date_init', 'date_end', 'delta')
    def _compute_delta(self):
        for rec in self:
            if rec.date_init and rec.date_end:

                # rec.delta = (((rec.date_end.hour * 3600) + (rec.date_end.minute * 60) + rec.date_end.second) \
                # - ((rec.date_init.hour * 3600) + (rec.date_init.minute * 60) + rec.date_init.second)) / 3600
                rec.delta = (rec.date_end - rec.date_init).total_seconds() / 3600
            else:
                rec.delta = 0


class projectTask(models.Model):
    _inherit = 'project.task'

    #     planned_hours_compute = fields.Float("Horas planeadas 2", help='Time planned to achieve this task (including its sub-tasks).', tracking=True, compute = 'get_planned_hours_compute')

    start_date_w = fields.Date(string="Start Date")
    end_date_w = fields.Date(string="End Date")

    binacle_ids = fields.One2many('project.binacle', 'parent_id', string='Bitacora')
    model_fleet_id = fields.Many2one('fleet.vehicle.model', string='Modelo/Grua')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Grua')

    start_odometer = fields.Float(string='Start Odometer',
                                  help='Odometer measure of the vehicle at the moment of this log')
    start_odometer_unit = fields.Selection([
        ('kilometers', 'km'),
        ('miles', 'mi')
    ], 'Odometer Unit', default='kilometers', help='Unit of the odometer ', required=True)

    end_odometer = fields.Float(string='End Odometer', help='Odometer measure of the vehicle at the moment of this log',
                                compute='_calculate_end_odometer')
    end_odometer_unit = fields.Selection([
        ('miles', 'mi')
    ], 'Odometer Unit', default='miles', help='Unit of the odometer ', required=True)

    start_hourmeter = fields.Float(string='Start Hourmeter',
                                   help='Hourmeter measure of the vehicle at the moment of this log')
    start_hourmeter_unit = fields.Selection([
        ('hours', 'hrs'),
    ], 'hourmeter Unit', default='hours', help='Unit of the hourmeter ', required=True)

    end_hourmeter = fields.Float(string='End Hourmeter',
                                 help='horometer measure of the vehicle at the moment of this log',
                                 compute='_calculate_end_hourmeter')
    end_hourmeter_unit = fields.Selection([
        ('hours', 'hrs'),
    ], 'Hourmeter Unit', default='hours', help='Unit of the hourmeter', required=True)

    accumulated_odometer = fields.Float(string='Odometro acumulado', compute='_calculate_odometer')
    accumulated_hourmeter = fields.Float(string='Horometro acumulado', compute='_calculate_hourmeter')

    def reset_binacle_ids(self):
        #         return
        self.end_date_w = False
        self.start_date_w = False

    def get_binacle_ids(self):

        if self.start_date_w and self.end_date_w:
            user_tz = self.env.user.tz or pytz.utc

            return self.binacle_ids.filtered(
                lambda l: self.start_date_w <= (
                    l.date_init.astimezone(pytz.timezone(user_tz))).date() <= self.end_date_w)
        else:
            return self.binacle_ids

    def action_report_domain(self):
        return {
            'name': 'Reporte diario',
            'type': 'ir.actions.act_window',
            'res_model': 'dayli.operations.report.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        result = super(projectTask, self).create(vals)

        if result.sale_order_id:
            total_hours = 0
            for line in result.sale_order_id.order_line:
                total_hours += line.product_uom_qty

            result.planned_hours = total_hours
        return result

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.start_odometer = self.vehicle_id.odometer
            self.start_odometer_unit = self.vehicle_id.odometer_unit
            self.start_hourmeter = self.vehicle_id.start_hourmeter
            self.start_hourmeter_unit = self.vehicle_id.start_hourmeter_unit
        else:
            self.start_odometer = 0.00
            self.start_odometer_unit = False
            self.start_hourmeter = 0.00
            self.start_hourmeter_unit = False

    @api.constrains('binacle_ids')
    def _check_binacle_ids(self):
        # CODE HERE
        for line in self.binacle_ids:
            res = sum(self.binacle_ids.filtered(lambda x: x.product_id == line.product_id).mapped('delta'))

            if res > sum(self.sale_order_id.order_line.filtered(lambda x: x.product_id == line.product_id).mapped(
                    'product_uom_qty')):
                raise ValidationError(
                    'El registro de horas no puede ser mayor a las horas cotizadas si se necesitan más horas, '
                    'el administrador deberá agregar horas a la cotización.')

    def action_fsm_validate(self):
        super().action_fsm_validate()

        timesheet_ids = []

        for line in self.binacle_ids:
            if line.gruero_id:
                # Registro Gruero

                timesheet_ids.append((0, 0, {
                    'date': line.date_init.date(),
                    # 'x_studio_hora_inicio': line.date_init.date(),
                    'employee_id': line.gruero_id.id,
                    'name': line.comment,
                    'unit_amount': line.delta,
                }))
            if line.support_id:
                # Registro Ayudante
                timesheet_ids.append((0, 0, {
                    'date': line.date_init.date(),
                    # 'x_studio_hora_inicio': line.date_init.date(),
                    'employee_id': line.support_id.id,
                    'name': line.comment,
                    'unit_amount': line.delta,
                }))

        # Crea registro del horometro en el vehículo
        self.env['fleet.vehicle.hourmeter'].create({
            'date': date.today(),
            'value': self.end_hourmeter,
            'unit': self.end_hourmeter_unit,
            'vehicle_id': self.vehicle_id.id,
        })

        self.vehicle_id.start_hourmeter = self.end_hourmeter
        # self.vehicle_id.odometer = self.end_odometer
        self.vehicle_id.write({'odometer': self.end_odometer, 'odometer_unit': self.end_odometer_unit})

        self.timesheet_ids = timesheet_ids

    @api.depends('binacle_ids.odometer')
    def _calculate_odometer(self):
        self.accumulated_odometer = 0
        for line in self.binacle_ids:
            self.accumulated_odometer += line.odometer

    @api.depends('binacle_ids.hourmeter')
    def _calculate_hourmeter(self):
        self.accumulated_hourmeter = 0
        for line in self.binacle_ids:
            self.accumulated_hourmeter += line.hourmeter

    @api.depends('accumulated_hourmeter')
    def _calculate_end_hourmeter(self):
        self.end_hourmeter = self.start_hourmeter + self.accumulated_hourmeter

    @api.depends('accumulated_odometer')
    def _calculate_end_odometer(self):
        self.end_odometer = self.start_odometer + self.accumulated_odometer

    # @api.model
    # def default_get(self, fields):
    #   res = super(projectTask, self).default_get(fields)

    # context = dict(self.env.context)
    #   context.update({'current_model':self , 'active_id':self.id})
    #  self.env.context = context

    # raise ValidationError(self._context)
    # return res
