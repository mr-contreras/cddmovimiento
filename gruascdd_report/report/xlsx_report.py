import json
import logging
from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class projectTaskXlsx(models.AbstractModel):
    _name = 'report.project.task.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        USD = 2
        MXN = 33
        cantidad = 1
        sheet = workbook.add_worksheet('')

        # Formatos
        f_report_header = workbook.add_format({
            'font_size': 14,
            'bottom': True, 'right': True, 'left': True, 'top': True,
            'align': 'center',
            'bold': True
        })
        f_report_date = workbook.add_format({
            'font_size': 10, 'align': 'left',
            'right': False, 'left': False, 'bottom': False, 'top': False,
            'bold': True,
            'text_wrap': True
        })
        f_table_header = workbook.add_format({
            'font_size': 12,
            'bold': True, 'border': 1,
            'valign': 'top', 'align': 'center',
            'text_wrap': 'true'
        })
        f_table_cell_text = workbook.add_format({
            'font_size': 12,
            'align': 'left',
            'text_wrap': 'true'
        })
        f_table_cell_date = workbook.add_format({
            'font_size': 12,
            'align': 'right',
            'num_format': 'dd/mm/yyyy hh:mm AM/PM'
        })
        f_table_cell_money = workbook.add_format({
            'font_size': 12,
            'align': 'right',
            'num_format': '$#,##0.00'
        })
        f_table_cell_number = workbook.add_format({
            'font_size': 12,
            'align': 'right',
        })

        # Encabezado de reporte
        sheet.merge_range('A2:V2', self.env.user.company_id.name, f_report_header)
        sheet.merge_range('A3:V3', 'Resumen de actividades', f_report_header)
        sheet.merge_range('A5:D5',
                          _("Fecha de impresión: " +
                            datetime.today().replace(microsecond=0).strftime('%d-%m-%Y %H:%M:%S')),
                          f_report_date)

        # Encabezadode la tabla
        sheet.set_column('A:C', 15)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:G', 35)
        sheet.set_column('H:I', 25)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 30)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:U', 25)
        sheet.set_column('V:W', 15)
        sheet.set_column('X:X', 40)
        sheet.set_column('Y:Y', 16)
        sheet.set_column('Z:Z', 40)
        sheet.set_column('AA:AA', 16)
        sheet.set_column('AB:AB', 40)
        sheet.set_column('AC:AC', 16)

        y_title = 6  # 8
        sheet.write(y_title, 0, 'Trabajo #', f_table_header)
        sheet.write(y_title, 1, 'Folio #', f_table_header)
        sheet.write(y_title, 2, 'Número de contrato (GSM)', f_table_header)
        sheet.write(y_title, 3, 'Grúa # ', f_table_header)

        sheet.write(y_title, 4, 'Nombre tarea', f_table_header)
        sheet.write(y_title, 5, 'Cliente', f_table_header)
        sheet.write(y_title, 6, 'Locación', f_table_header)

        sheet.write(y_title, 7, 'Inicio', f_table_header)
        sheet.write(y_title, 8, 'Final', f_table_header)

        sheet.write(y_title, 9, 'Total Horas', f_table_header)

        sheet.write(y_title, 10, 'Detalle ', f_table_header)

        sheet.write(y_title, 11, 'Cantidad de Grúas', f_table_header)

        sheet.write(y_title, 12, 'Precio MXN', f_table_header)
        sheet.write(y_title, 13, 'Sub Total MXN', f_table_header)
        sheet.write(y_title, 14, 'IVA MXN', f_table_header)
        sheet.write(y_title, 15, 'Total MXN', f_table_header)
        sheet.write(y_title, 16, 'Precio USD', f_table_header)
        sheet.write(y_title, 17, 'Sub Total USD', f_table_header)
        sheet.write(y_title, 18, 'IVA USD', f_table_header)
        sheet.write(y_title, 19, 'Total USD', f_table_header)
        sheet.write(y_title, 20, 'Pagado MXN', f_table_header)

        sheet.write(y_title, 21, 'Estatus de cotización', f_table_header)
        sheet.write(y_title, 22, 'Estatus operativo', f_table_header)

        sheet.write(y_title, 23, 'Operador de Grúa', f_table_header)
        sheet.write(y_title, 24, 'Horas Generadas Operador', f_table_header)
        sheet.write(y_title, 25, 'Ayudante de Grúa', f_table_header)
        sheet.write(y_title, 26, 'Horas Generadas Ayudante', f_table_header)
        sheet.write(y_title, 27, 'Tercer Ayudante de Grúa', f_table_header)
        sheet.write(y_title, 28, 'Horas Generadas Tercer Ayudante', f_table_header)

        # Obtener los registros
        if data:
            options = json.loads(data['options'])
            if options['date_filtered_init']:
                options['date_filtered_init'] = datetime.strptime(options['date_filtered_init'], '%Y-%m-%d %H:%M:%S')
            if options['date_filtered_end']:
                options['date_filtered_end'] = datetime.strptime(options['date_filtered_end'], '%Y-%m-%d %H:%M:%S')

            if options['type_filtered'] == 'state':
                objs = self.env['sale.order'].search([
                    '&', ('active_task', '=', True), ('state', '=', options['state'])
                ])
            elif options['type_filtered'] == 'uni_eco':
                _logger.info("Unidad: %s", options['vehicle_id'])
                objs = self.env['sale.order'].search([
                    '&', ('active_task', '=', True), ('vehicle_id', '=', options['vehicle_id'])
                ])
            elif options['type_filtered'] == 'date_create':
                objs = self.env['sale.order'].search([
                    '&', '&', ('active_task', '=', True),
                    ('date_order', '>', options['date_filtered_init']),
                    ('date_order', '<', options['date_filtered_end'])
                ])
            elif options['type_filtered'] == 'date_ejec':
                objs = self.env['sale.order'].search([
                    '&', '&', ('active_task', '=', True),
                    ('task_date_last_stage_update', '>', options['date_filtered_init']),
                    ('task_date_last_stage_update', '<', options['date_filtered_end'])
                ])
            elif options['type_filtered'] == 'all':
                objs = self.env['sale.order'].search([
                    ('active_task', '=', True)
                ])

        y_title += 1

        # Llenando latabla
        for rec in objs.sorted(lambda x: x.name, reverse=True):
            horas = 0
            products = []

            if rec.tasks_ids:
                # _logger.info("#####################Orden: %s", rec.name)
                for binnacle in rec.tasks_ids[0].binnacle_ids:
                    # _logger.info("Biacle %s, %s, %f", binacle.gruero_id.mapped('name'), binacle.support_id.mapped('name'), binacle.delta)
                    horas += binnacle.delta

                    products.append(binnacle.product_id.id)

            unique_products = (list(set(products)))

            payment_state = 'Sin Facturar'

            if rec.invoice_ids:
                if rec.invoice_ids[0].payment_state == 'not_paid':
                    payment_state = 'Sin pagar'
                elif rec.invoice_ids[0].payment_state == 'in_payment':
                    payment_state = 'En Proceso de Pago'
                elif rec.invoice_ids[0].payment_state == 'paid':
                    payment_state = 'Pagado'
                elif rec.invoice_ids[0].payment_state == 'partial':
                    payment_state = 'Pagado Parcialmente'
                elif rec.invoice_ids[0].payment_state == 'reversed':
                    payment_state = 'Revertido'
                elif rec.invoice_ids[0].payment_state == 'invoicing_legacy':
                    payment_state = 'Sistema anterior de facturacion'
                # ayudantes = rec.tasks_ids[0].user_ids.filtered(lambda x : x.type_employee == 'support').mapped('name')

            if rec.tasks_ids:

                for task in rec.tasks_ids[0]:

                    for product in task.binnacle_ids:
                        product_name = rec.tasks_ids[0].binnacle_ids.filtered(
                            lambda u: u.product_id.id == product.product_id.id)
                        order_line = rec.order_line.filtered(lambda u: u.product_id.id == product.product_id.id)

                        if order_line[0].product_uom_qty == 0:
                            cantidad = 1
                        else:
                            cantidad = order_line[0].product_uom_qty

                        product_price_subtotal = sum(
                            rec.order_line.filtered(lambda u: u.product_id.id == product.product_id.id).mapped(
                                'price_subtotal')) / cantidad
                        product_price_iva = sum(
                            rec.order_line.filtered(lambda u: u.product_id.id == product.product_id.id).mapped(
                                'price_tax')) / cantidad

                        sheet.write(y_title, 0, rec.name, f_table_cell_text)
                        sheet.write(y_title, 1, product.folio if product.folio else '', f_table_cell_text)
                        sheet.write(y_title, 2,
                                    rec.tasks_ids[0].x_studio_contrato if rec.tasks_ids[0].x_studio_contrato else ' ',
                                    f_table_cell_text)
                        sheet.write(y_title, 3, product.vehicle_id.x_studio_numero_economico if product else '',
                                    f_table_cell_text)
                        sheet.write(y_title, 4, rec.tasks_ids[0].name if rec.tasks_ids else '', f_table_cell_text)
                        sheet.write(y_title, 5, rec.partner_id.name, f_table_cell_text)
                        sheet.write(y_title, 6, rec.pozo, f_table_cell_text)
                        sheet.write(y_title, 7, product.date_init.strftime('%d-%m-%Y %H:%M:%S'), f_table_cell_date)
                        sheet.write(y_title, 8, product.date_end.strftime('%d-%m-%Y %H:%M:%S'), f_table_cell_date)
                        sheet.write(y_title, 9, product.delta, f_table_cell_number)
                        sheet.write(y_title, 10, product.product_id.name if product_name else ' ', f_table_cell_text)
                        sheet.write(y_title, 11, 1, f_table_cell_number)

                        if order_line[0].currency_id.id == MXN:
                            sheet.write(y_title, 12, order_line[0].price_unit if order_line else '', f_table_cell_money)
                            sheet.write(y_title, 13, product_price_subtotal, f_table_cell_money)
                            sheet.write(y_title, 14, product_price_iva, f_table_cell_money)
                            sheet.write(y_title, 15, (product_price_subtotal + product_price_iva), f_table_cell_money)
                            sheet.write(y_title, 16, 0.00, f_table_cell_money)
                            sheet.write(y_title, 17, 0.00, f_table_cell_money)
                            sheet.write(y_title, 18, 0.00, f_table_cell_money)
                            sheet.write(y_title, 19, 0.00, f_table_cell_money)
                        elif order_line[0].currency_id.id == USD:
                            sheet.write(y_title, 12, 0.00, f_table_cell_money)
                            sheet.write(y_title, 13, 0.00, f_table_cell_money)
                            sheet.write(y_title, 14, 0.00, f_table_cell_money)
                            sheet.write(y_title, 15, 0.00, f_table_cell_money)
                            sheet.write(y_title, 16, order_line[0].price_unit if order_line else '', f_table_cell_money)
                            sheet.write(y_title, 17, product_price_subtotal, f_table_cell_money)
                            sheet.write(y_title, 18, product_price_iva, f_table_cell_money)
                            sheet.write(y_title, 19, (product_price_subtotal + product_price_iva), f_table_cell_money)

                        sheet.write(y_title, 20, rec.get_paid_ammount(), f_table_cell_money)
                        sheet.write(y_title, 21, payment_state, f_table_cell_text)
                        sheet.write(y_title, 22, rec.tasks_ids[0].stage_id.name, f_table_cell_text)
                        sheet.write(y_title, 23, product.gruero_id.name if product.gruero_id else ' ',
                                    f_table_cell_text)
                        sheet.write(y_title, 24, product.delta if product.gruero_id else 0.00, f_table_cell_number)
                        sheet.write(y_title, 25, product.ayudante_id.name if product.ayudante_id else ' ',
                                    f_table_cell_text)
                        sheet.write(y_title, 26, product.delta if product.ayudante_id else 0.00, f_table_cell_number)
                        sheet.write(y_title, 27, product.tercer_ayudante_id.name if product.tercer_ayudante_id else ' ',
                                    f_table_cell_text)
                        sheet.write(y_title, 28, product.delta if product.tercer_ayudante_id else 0.00,
                                    f_table_cell_number)

                        y_title += 1