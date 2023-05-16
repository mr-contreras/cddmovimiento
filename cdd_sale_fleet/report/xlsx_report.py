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

        sheet = workbook.add_worksheet('')

        #Formatos
        f_report_header = workbook.add_format({
            'font_size': 14,
            'bottom': True, 'right': True, 'left': True, 'top': True,
            'align': 'center',
            'bold': True
        })
        f_report_date = workbook.add_format({
            'font_size': 10, 'align': 'left',
            'right': False, 'left': False,'bottom': False, 'top': False,
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

        #Encabezado de reporte
        sheet.merge_range('A2:V2', self.env.user.company_id.name, f_report_header)
        sheet.merge_range('A3:V3','Resumen de actividades', f_report_header)
        sheet.merge_range('A5:D5',
                          _("Fecha de impresión: " +
                            datetime.today().replace(microsecond=0).strftime('%d-%m-%Y %H:%M:%S')),
                          f_report_date)

        # Encabezadode la tabla
        sheet.set_column('A:C', 15)
        sheet.set_column('D:F', 30)
        sheet.set_column('G:H', 25)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 30)
        sheet.set_column('K:R', 15)
        sheet.set_column('S:V', 30)

        y_title = 6 # 8
        sheet.write(y_title, 0, 'Trabajo #', f_table_header)
        sheet.write(y_title, 1, 'Número de contrato (GSM)', f_table_header)
        sheet.write(y_title, 2, 'Grúa # ', f_table_header)
        sheet.write(y_title, 3, 'Nombre tarea', f_table_header)
        sheet.write(y_title, 4, 'Cliente', f_table_header)
        sheet.write(y_title, 5, 'Locación', f_table_header)
        sheet.write(y_title, 6, 'Inicio', f_table_header)
        sheet.write(y_title, 7, 'Final', f_table_header)

        sheet.write(y_title, 8, 'Total Horas', f_table_header)
        sheet.write(y_title, 9, 'Detalle ', f_table_header)
        sheet.write(y_title, 10, 'Precio', f_table_header)
        sheet.write(y_title, 11, 'Cantidad de Grúas', f_table_header)
        sheet.write(y_title, 12, 'Sub Total', f_table_header)
        sheet.write(y_title, 13, 'IVA', f_table_header)
        
        sheet.write(y_title, 14, 'Total', f_table_header)
        sheet.write(y_title, 15, 'Pagado', f_table_header)
        sheet.write(y_title, 16, 'Estatus de cotización', f_table_header)
        sheet.write(y_title, 17, 'Estatus operativo', f_table_header)
        sheet.write(y_title, 18, 'Operador de Grúa Guardia #1', f_table_header)
        sheet.write(y_title, 19, 'Horas Generadas Guardia #1', f_table_header)

        sheet.write(y_title, 20, 'Ayudante Grua Guardia #1', f_table_header)
        sheet.write(y_title, 21, 'Horas Generadas Guardia #1', f_table_header)

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
            str_grueros = ''
            grueros = []
            supports = []
            horas = 0
            products = []
            
            if rec.tasks_ids:
                # _logger.info("#####################Orden: %s", rec.name)
                for binacle in rec.tasks_ids[0].binacle_ids:
                    # _logger.info("Biacle %s, %s, %f", binacle.gruero_id.mapped('name'), binacle.support_id.mapped('name'), binacle.delta)
                    for gruero in binacle.gruero_id.mapped('name'):
                        if gruero not in grueros:
                            grueros.append(gruero)
                    for support in binacle.support_id.mapped('name'):
                        if support not in supports:
                            supports.append(support)
                    horas += binacle.delta
                    
                    products.append(binacle.product_id.id)
            
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
                    bandera = False
                    
                    for product in task.binacle_ids:
                        if product.product_id.id in unique_products:
                            bandera = True
                            break
                            
                    if bandera:
                        for line in unique_products: 
                            product_name = rec.tasks_ids[0].binacle_ids.filtered(lambda u: u.product_id.id == line)
                            product_price_unit = rec.order_line.filtered(lambda u: u.product_id.id == line)
                            product_price_subtotal = sum(rec.order_line.filtered(lambda u: u.product_id.id == line).mapped('price_subtotal'))
                            product_price_iva = sum(rec.order_line.filtered(lambda u: u.product_id.id == line).mapped('price_tax'))

                            sheet.write(y_title, 0, rec.name, f_table_cell_text)
                            sheet.write(y_title, 1, rec.tasks_ids[0].x_studio_contrato if rec.tasks_ids else '', f_table_cell_text)
                            sheet.write(y_title, 2, rec.tasks_ids[0].vehicle_id.x_studio_numero_economico if rec.tasks_ids else '', f_table_cell_text)
                            sheet.write(y_title, 3, rec.tasks_ids[0].name if rec.tasks_ids else '', f_table_cell_text)
                            sheet.write(y_title, 4, rec.partner_id.name, f_table_cell_text)
                            sheet.write(y_title, 5, rec.nombre_pozo, f_table_cell_text)                              
                            sheet.write(y_title, 6, rec.get_date_init_2(line).strftime('%d-%m-%Y %H:%M:%S'), f_table_cell_date)
                            sheet.write(y_title, 7, rec.get_date_end_2(line).strftime('%d-%m-%Y %H:%M:%S'), f_table_cell_date)
                            sheet.write(y_title, 8, rec.get_total_hours_2(line), f_table_cell_number)
                            sheet.write(y_title, 9, product_name[0].product_id.name if product_name else '', f_table_cell_text)
                            sheet.write(y_title, 10, product_price_unit[0].price_unit if product_price_unit else '', f_table_cell_money)
                            sheet.write(y_title, 11, 1, f_table_cell_number)
                            sheet.write(y_title, 12, product_price_subtotal, f_table_cell_money)
                            sheet.write(y_title, 13, product_price_iva, f_table_cell_money)
                            sheet.write(y_title, 14, (product_price_subtotal + product_price_iva), f_table_cell_money)
                            sheet.write(y_title, 15, rec.get_paid_ammount(), f_table_cell_money)
                            sheet.write(y_title, 16, payment_state, f_table_cell_text)
                            sheet.write(y_title, 17, rec.tasks_ids[0].stage_id.name, f_table_cell_text)
                            sheet.write(y_title, 18, ", ".join(grueros) if rec.tasks_ids else '', f_table_cell_text)
                            sheet.write(y_title, 19, horas, f_table_cell_number)
                            sheet.write(y_title, 20, ", ".join(supports) if rec.tasks_ids else '', f_table_cell_text)
                            sheet.write(y_title, 21, horas, f_table_cell_number)
                            y_title += 1
                    else:
                        sheet.write(y_title, 0, rec.name, f_table_cell_text)
                        sheet.write(y_title, 1, rec.tasks_ids[0].x_studio_contrato if rec.tasks_ids else '', f_table_cell_text)
                        sheet.write(y_title, 2, rec.tasks_ids[0].vehicle_id.x_studio_numero_economico if rec.tasks_ids else '', f_table_cell_text)
                        sheet.write(y_title, 3, rec.tasks_ids[0].name if rec.tasks_ids else '', f_table_cell_text)
                        sheet.write(y_title, 4, rec.partner_id.name, f_table_cell_text)
                        sheet.write(y_title, 5, rec.nombre_pozo, f_table_cell_text)                           
                        sheet.write(y_title, 6, '', f_table_cell_date)
                        sheet.write(y_title, 7, '', f_table_cell_date)
                        sheet.write(y_title, 8, 0, f_table_cell_number)
                        sheet.write(y_title, 9, '', f_table_cell_text)
                        sheet.write(y_title, 10, 0, f_table_cell_money)
                        sheet.write(y_title, 11, 0, f_table_cell_number)
                        sheet.write(y_title, 12, 0, f_table_cell_money)
                        sheet.write(y_title, 13, 0, f_table_cell_money)
                        sheet.write(y_title, 14, 0, f_table_cell_money)
                        sheet.write(y_title, 15, rec.get_paid_ammount(), f_table_cell_money)
                        sheet.write(y_title, 16, payment_state, f_table_cell_text)
                        sheet.write(y_title, 17, task.stage_id.name, f_table_cell_text)
                        sheet.write(y_title, 18, ", ".join(grueros) if rec.tasks_ids else '', f_table_cell_text)
                        sheet.write(y_title, 19, horas, f_table_cell_number)
                        sheet.write(y_title, 20, ", ".join(supports) if rec.tasks_ids else '', f_table_cell_text)
                        sheet.write(y_title, 21, horas, f_table_cell_number) 
                        
                        y_title += 1
                        
                    
