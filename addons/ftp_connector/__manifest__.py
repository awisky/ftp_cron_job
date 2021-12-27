# © Agustin Wisky
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "FTP Connector",
    "summary": "FTP/SFTP connector",
    "version": "15.0.1.0.0",
    "category": "Localization",
    'author': "Agustin wisky",
    'website': "",
    "depends": [
        'mail',
    ],
    "external_dependencies": {"python": [
        'pysftp',
    ]},
    "data": [
        "security/ir.model.access.csv",

        'views/ftp_connector_view.xml',
        'views/menuitem.xml',
    ],
    'demo': [
        'demo/ftp_demo.xml',
    ],
    'installable': True,
    'auto_install': False
}
