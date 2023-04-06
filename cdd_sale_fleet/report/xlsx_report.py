import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')




from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class projectTaskXlsx(models.AbstractModel):
    _name = 'report.project.task.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, obj):
        
        
        sheet = workbook.add_worksheet('')
        bold = workbook.add_format({'bold': True})
        
        textWrap_header = workbook.add_format({'text_wrap':'true', 'border': 1, 'valign': 'vcenter','bold': True,})
        textWrap = workbook.add_format({'text_wrap':'true', 'border': 1, 'valign': 'top'})
        textWrap_table = workbook.add_format({'text_wrap':'true'})
        floating_point_bordered = workbook.add_format({'num_format': '#,##0.00', 'border': 1,'valign': 'top'})
        
        bold_center = workbook.add_format({'bold': True})
        bold_center_border = workbook.add_format({'bold': True, 'border': 1})
        textWrap_header.set_align('center')
        bold_center_border.set_align('center')
        bold_center.set_align('center')
        money_format = workbook.add_format({'num_format': 'L#,##0.00'})
        bold_money_format = workbook.add_format({'num_format': 'L#,##0.00','bold': True})
        
        # Widen the first column to make the text clearer.
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 14)
        sheet.set_column('C:C', 14)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 14)
        sheet.set_column('F:F', 50)
        sheet.set_column('G:O', 10)

        company = self.env['res.company'].search([
            ('id','=',1)
        ])
       
        y_title = 1 # 8

    
        y_title += 5
        
        objs_n = self.env['sale.order'].sudo().search([
            ('id', '>', 0)
        ])
        
        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
                'bold': True})
        format4 = workbook.add_format({'align':'center', 'left':True, 'right':True, 'bottom': True, 'top': True, 'font_size': 10,'num_format': '#,##0.00', 'bold': True, 'bg_color':'#dbeb34'})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': True, 'font_color':'#ffffff','bg_color':'#000000'})
        format23 = workbook.add_format({'font_size': 10, 'align': 'left', 'right': False, 'left': False,'bottom': False, 'top': False, 'bold': True, 'text_wrap': True})
        format22 = workbook.add_format({'font_size': 10, 'align': 'left', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': False, 'text_wrap': True})
        format24 = workbook.add_format({'font_size': 10, 'align': 'left', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': False, 'text_wrap': True, 'num_format': '#,##0.00'})
        
        
        sheet.merge_range('A2:U2', self.env.user.company_id.name, format1)
        sheet.merge_range('A3:U3','Resumen de actividades', format1)
        sheet.merge_range('A5:D5', _("Fecha de impresión: "+datetime.today().replace(microsecond=0).strftime('%d-%m-%Y %H:%M:%S')),format23)
        
        sheet.write(y_title, 0, 'Trabajo #',bold_center_border)
        sheet.write(y_title, 1, 'Grua # ',bold_center_border)
        sheet.write(y_title, 2, 'Cliente',bold_center_border)
        sheet.write(y_title, 3, 'Locacion',bold_center_border)
        sheet.write(y_title, 4, 'Inicio',bold_center_border)
        sheet.write(y_title, 5, 'Final',bold_center_border)
        sheet.write(y_title, 6, 'Total dias',bold_center_border)
        
        sheet.write(y_title, 7, 'Total Horas',bold_center_border)
        sheet.write(y_title, 8, 'Detalle ',bold_center_border)
        sheet.write(y_title, 9, 'Precio',bold_center_border)
        sheet.write(y_title, 10, 'Cantidad',bold_center_border)
        sheet.write(y_title, 11, 'Sub Total',bold_center_border)
        sheet.write(y_title, 12, 'IVA',bold_center_border)
        
        sheet.write(y_title, 13, 'Total',bold_center_border)
        sheet.write(y_title, 14, 'Estatus de Pago',bold_center_border)
        sheet.write(y_title, 15, 'Estatus',bold_center_border)
        sheet.write(y_title, 16, 'Estatus operativo',bold_center_border)
        sheet.write(y_title, 17, 'Operador de Grua',bold_center_border)
        sheet.write(y_title, 18, 'Horas Generadas',bold_center_border)
        
        sheet.write(y_title, 19, 'Ayudante Grua',bold_center_border)
        sheet.write(y_title, 20, 'Horas Generadas',bold_center_border)
        y_title+=1
                
        for rec in objs_n.sorted(lambda x: x.name , reverse = True):
                
            #grueros = rec.tasks_ids[0].user_ids.filtered(lambda x : x.type_employee == 'gruero').mapped('name')
            str_grueros = ''
            if rec.tasks_ids:
                grueros_array = rec.tasks_ids[0].user_ids.mapped('name')
                for i in grueros_array: str_grueros+= (i + ' , ')
            
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
                #ayudantes = rec.tasks_ids[0].user_ids.filtered(lambda x : x.type_employee == 'support').mapped('name')

            for line in rec.order_line:
                                                               
                sheet.write(y_title, 0, rec.name ,textWrap_table)
                sheet.write(y_title, 1, rec.tasks_ids[0].vehicle_id.x_studio_numero_economico if rec.tasks_ids else '',textWrap_table)
                sheet.write(y_title, 2, rec.partner_id.name,textWrap_table)
                sheet.write(y_title, 3, '',textWrap_table)
                sheet.write(y_title, 4, rec.date_order.strftime('%d-%m-%Y %H:%M:%S'),textWrap_table)
                sheet.write(y_title, 5, rec.date_order.strftime('%d-%m-%Y %H:%M:%S'),textWrap_table)
                sheet.write(y_title, 6, rec.tasks_ids[0].working_days_open  if rec.tasks_ids else '' ,textWrap_table)

                sheet.write(y_title, 7, rec.tasks_ids[0].working_hours_open if rec.tasks_ids else '' ,textWrap_table)
                sheet.write(y_title, 8, line.name,textWrap_table)
                sheet.write(y_title, 9, line.price_unit,textWrap_table)
                sheet.write(y_title, 10, line.product_uom_qty,textWrap_table)
                sheet.write(y_title, 11, line.price_subtotal,textWrap_table)
                sheet.write(y_title, 12, line.price_tax ,textWrap_table)

                sheet.write(y_title, 13, (line.price_subtotal + line.price_tax) ,textWrap_table)
                sheet.write(y_title, 14, payment_state,textWrap_table)
                sheet.write(y_title, 15, rec.state ,textWrap_table)
                sheet.write(y_title, 16, rec.tasks_ids[0].stage_id.name if rec.tasks_ids else '',textWrap_table)
                sheet.write(y_title, 17, str_grueros if rec.tasks_ids else '',textWrap_table)
                sheet.write(y_title, 18, '',textWrap_table)

                sheet.write(y_title, 19, str_grueros if rec.tasks_ids else '',textWrap_table)
                sheet.write(y_title, 20, '',textWrap_table)
                y_title+=1
        