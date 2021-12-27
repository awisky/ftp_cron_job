# © 2021 Agustin Wisky
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import base64
import io
import pytz
from datetime import datetime
from odoo import models, fields, api, exceptions, _
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)

DEVICE = ["external_id", "name", "description", "code", "expire_date", "state"]
CONTENT = [
    "external_id", "name", "description", "device_id", "expire_date", "state"
]
STATES = [
    ('enabled', 'Enabled'), ('disabled', 'Disabled'), ('deleted', 'Deleted')
]


class DeviceAbstract(models.AbstractModel):
    """
    Abstract model for devices data models
    """
    _name = 'device.abstract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Device Absgtract"
    _rec_name = 'external_id'

    external_id = fields.Integer()
    name = fields.Char(size=32)
    description = fields.Char(size=128)
    expire_date = fields.Datetime()
    state = fields.Selection(selection=STATES, default='enabled')


class Device(models.Model):
    """
    Device Model
    """
    _name = 'device.device'
    _inherit = ['device.abstract']
    _description = "Device"

    code = fields.Char(size=30)
    content_ids = fields.One2many('device.content', 'device_id')

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code must be unique for device.'),
    ]


class DeviceContent(models.Model):
    """
    Device Content Model
    """
    _name = 'device.content'
    _inherit = ['device.abstract']
    _description = "Device Content"

    name = fields.Char(size=100)
    device_id = fields.Many2one('device.device', ondelete='cascade')

    _sql_constraints = [
        ('unique_external_id', 'unique(external_id, device_id)',
         'This External ID content is already used'),
    ]


class DeviceJob(models.Model):
    """
    Device Cron Job
    """

    _name = 'device.job'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Device Job"

    name = fields.Char()

    job_type = fields.Selection(
        selection=[('file', 'File'), ('ftp', 'FTP')], default='ftp'
    )

    ftp_id = fields.Many2one('ftp.connector')

    device_attachment_id = fields.Many2one('ir.attachment')
    device_file_path = fields.Char(help="File path")

    content_attachment_id = fields.Many2one('ir.attachment')
    content_file_path = fields.Char(help="File path")

    run_active = fields.Boolean()

    def get_file_values(self, datas=None, header=None):
        """
        Return values from file
        """
        if not datas or not header:
            return False
        try:
            data = base64.b64decode(datas)
            reader = pycompat.csv_reader(
                io.BytesIO(data), quotechar='"', delimiter=','
            )
            values = list(reader)
        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError(
                _("Something went wrong, please make sure that you selected "
                  "a none corrupted file."))
        return map(lambda value: dict((zip(header, value))), values)

    def _parse_external_id(self, external_id):
        """
        Parsing the external id to integer
        """
        try:
            external_id = int(external_id.strip())
        except Exception as e:
            external_id = 0
            _logger.error(e)
        return external_id

    def _parse_expire_date(self, expire_date):
        """
        Parsing datetime from iso format
        """
        user_utc = pytz.timezone(self.env.user.tz)
        expire_date = expire_date and expire_date.strip()

        try:
            expire_date = datetime.fromisoformat(expire_date)
            expire_date = expire_date.astimezone(user_utc).replace(tzinfo=None)
        except Exception as e:
            expire_date = False
            _logger.error(e)
        return expire_date

    def _parse_state(self, state, expire_date):
        """
        Parsing the state considering valid states and the expire date
        """
        state = state and state.strip()
        # check if the expire date is in the past to set the disabled state
        if expire_date and expire_date < fields.Datetime.now():
            state = 'disabled'

        # check if the state found is correct
        if not any(state in i for i in STATES):
            state = 'disabled'
        return state

    def _parse_code(self, code):
        """
        Parsing clean code
        """
        return code and code.strip()

    def _parse_device(self, device_id):
        """
        Parsing device
        """
        device_obj = self.env['device.device']
        try:
            device_id = int(device_id.strip())
        except Exception as e:
            device_id = 0
            _logger.error(e)
        device_id = device_obj.search(
            [('external_id', '=', device_id)], limit=1
        ).id
        return device_id

    def _get_clean_values(self, datas=None, header=None):
        """
        Return clean up values
        """
        if not datas or not header:
            return False

        values = self.get_file_values(datas=datas, header=header)
        _logger.info(_("Getting clean values..."))

        clean = []
        for row, value in enumerate(values):
            _logger.info(_("Processing row: %s " % row))
            _value = {}
            for key in header:
                _value[key] = value.pop(key) if key in value else ''

            external_id = self._parse_external_id(
                external_id=_value['external_id']
            )
            expire_date = self._parse_expire_date(
                expire_date=_value['expire_date']
            )
            state = self._parse_state(
                state=_value['state'], expire_date=expire_date
            )
            _value.update({
                'external_id': external_id,
                'state': state,
                'expire_date': expire_date,
            })
            if 'code' in _value:
                _value['code'] = self._parse_code(code=_value['code'])

            if 'device_id' in _value:
                device_id = self._parse_device(device_id=_value['device_id'])
                _value['device_id'] = device_id
            clean.append(_value)
        return clean

    def process_device_file(self):
        """
        Function to process the device file
        """
        _logger.info('Processing device file...')
        if not self.device_attachment_id:
            _logger.error(_("No device file"))
            return
        datas = self.device_attachment_id.datas
        header = DEVICE

        values = self._get_clean_values(datas=datas, header=header)
        device_obj = self.env['device.device']
        for value in values:
            code = value['code']
            external_id = value['external_id']
            device_id = device_obj.search([('code', '=', code)], limit=1)
            if not device_id and code and external_id:
                device_id = device_obj.create(value)

    def process_content_file(self, ):
        """
        Function to process the content file
        """
        _logger.info('Processing content file...')
        if not self.content_attachment_id:
            _logger.error(_("No content file"))
            return
        datas = self.content_attachment_id.datas
        header = CONTENT

        values = self._get_clean_values(datas=datas, header=header)

        content_obj = self.env['device.content']
        for value in values:
            device_id = value['device_id']
            external_id = value['external_id']
            if external_id and device_id:
                content_id = content_obj.search(
                    [
                     ('external_id', '=', external_id),
                     ('device_id', '=', device_id)
                    ], 
                    limit=1
                )
                if not content_id:
                    content_id = content_obj.create(value)

    def get_file(self, filename='text.txt'):
        """
        Return an attachment from a localfile
        """
        attachment_id = None
        _logger.info('Getting local file: %s' % filename)

        with open(filename, 'rb') as f:
            try:
                data = f.read()
                if data:
                    attachment_id = self.env['ir.attachment'].create({
                        'name': filename,
                        'type': 'binary',
                        'datas': base64.b64encode(data)
                    })
                    _logger.info('Attachment created: %s' % attachment_id)
                else:
                    _logger.error('No File: %s' % filename)

            except Exception as e:
                _logger.error('Local File Fault Detail: %s' % e)
            return attachment_id

    def action_download_files(self):
        """
        Function to download the file from ftp and store it as attachment
        """
        _logger.info('Downloading files...')
        if self.job_type == 'ftp':
            self.device_attachment_id = self.ftp_id.get_file(
                self.device_file_path
            )
            self.content_attachment_id = self.ftp_id.get_file(
                self.content_file_path
            )
        else:
            self.device_attachment_id = self.get_file(self.device_file_path)
            self.content_attachment_id = self.get_file(self.content_file_path)

    def action_process_files(self):
        self.process_device_file()
        self.process_content_file()

    def action_run_job(self):
        self.action_download_files()
        self.action_process_files()

    @api.model
    def _process_job_files(self, limit=10):
        """
        Run the active jobs with a limit per run
        """
        return self.search(
            [('run_active', '!=', False)], limit=limit
        ).action_run_job()
