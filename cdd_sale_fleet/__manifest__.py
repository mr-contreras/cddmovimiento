# -*- coding: utf-8 -*-
{
    'name': "CDD Sale Fleet",

    'summary': """ Modulo que automatiza multiples lineas de una orden de venta, en una sola tarea y un solo proyecto.""",

    'description': """
        Crea un sola tarea con multiples lineas de orden, para gestionar horas  de trabajo  de maquinaria y personas.
    """,

    'author': "Victor Amaya",
    'website': "https://ezzquad.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '1.0',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base','project','sale','sale_project','hr','hr_timesheet', 'report_xlsx','industry_fsm', 'account_move'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_hourmeter.xml',
        'views/hr_employee.xml',
        'views/project_task.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/view_task_form2_inherited.xml',
        'views/view_task_form2_inherited.xml',
        'report/sale_order_report.xml',
        'wizard/dayli_operations_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
