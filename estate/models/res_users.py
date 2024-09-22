from odoo import models,fields
from odoo.fields import One2many


class ResUsers(models.Model):
    _inherit = 'res.users'

    property_ids = One2many('estate.property','salesman_id',domain=[('state','in',['new','offer_received'])])