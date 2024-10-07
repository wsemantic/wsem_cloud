from odoo import http
from odoo.http import request
from odoo.service import db
from odoo import api, SUPERUSER_ID
import odoo
import ovh
import logging
import re

_logger = logging.getLogger(__name__)
