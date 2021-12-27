# © Agustin Wisky
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import ftplib
import io
from odoo import api, fields, models
import base64
import logging

_logger = logging.getLogger(__name__)


class FTPConnector(models.Model):
    _name = "ftp.connector"
    _description = "FTP Connector"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.onchange('connection_type')
    def _onchange_connection_type(self):
        for server in self:
            if server.connection_type == 'sftp':
                server.port = 22
            if server.connection_type == 'ftp':
                server.port = 21

    name = fields.Char(required=True, tracking=True)
    host = fields.Char(required=True, tracking=True)
    port = fields.Integer(tracking=True)
    user = fields.Char(required=True, tracking=True)
    password = fields.Char(required=True)
    active = fields.Boolean(default=True, tracking=True)
    connection_type = fields.Selection(
        [("sftp", "SFTP"), ("ftp", "FTP")],
        default="ftp",
        required="True",
        tracking=True
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('connect', 'Connect'), ('error', 'Error')],
        string="status",
        default='draft'
    )
    connect_message = fields.Text()

    def test_connection(self):
        with ftplib.FTP() as ftp:
            state = 'draft'
            msg = ""
            try:
                ftp.connect(self.host, self.port or 21)
                ftp.login(self.user, self.password)
                ftp.nlst()
                ftp.quit()
                state = 'connect'
                msg = "Congratulation, " \
                    "It's Successfully Connected with the FTP Server"
            except ftplib.all_errors as e:
                _logger.error('FTP Connector Fault Detail: %s' % e)
                msg = "FTP connection error, (%s) " % e
                state = 'error'
            return self.write({
                'connect_message': msg,
                'state': state,
            })

    def get_file(self, filename=None):
        attachment_id = None
        _logger.info('FTP getting file: %s' % filename)
        if not filename:
            return
        with ftplib.FTP() as ftp:
            try:
                ftp.connect(self.host, self.port or 21)
                ftp.login(self.user, self.password)
                download_file = io.BytesIO()
                data = ftp.retrbinary('RETR ' + filename, download_file.write)
                _logger.info('FTP File: %s %s' % (data, download_file))
                if data:
                    attachment_id = self.env['ir.attachment'].create({
                        'name': filename,
                        'type': 'binary',
                        'datas': base64.b64encode(download_file.getvalue())
                    })
                    _logger.info('Attachment created: %s' % attachment_id)
                else:
                    _logger.error('FTP Connector no File: %s' % filename)
                ftp.quit()

            except ftplib.all_errors as e:
                _logger.error('FTP Connector Fault Detail: %s' % e)
            return attachment_id
