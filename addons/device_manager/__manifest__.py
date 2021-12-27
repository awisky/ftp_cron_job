# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Device Manager',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': "Device Manager Module",
    'author': 'Agustin Wisky',
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'mail',
        'ftp_connector'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/menus_view.xml',
        'views/device_view.xml',
        'views/device_job_view.xml',
    ],
    'demo': [
        'demo/job_demo.xml',
    ],
    'installable': True,
    'auto_install': False
}
