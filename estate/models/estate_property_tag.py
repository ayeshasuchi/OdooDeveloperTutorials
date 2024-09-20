from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    color = fields.Integer()

    _sql_constraints = [
        ('check_name_uniq', 'unique(name)', "Name already exists!"),
    ]