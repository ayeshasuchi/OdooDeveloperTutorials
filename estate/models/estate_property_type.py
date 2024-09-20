from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "sequence,name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    property_ids = fields.One2many('estate.property','property_type_id')
    sequence = fields.Integer('Sequence', default=1, help="Used to order Type.")
    # For stat button:
    offer_ids = fields.One2many('estate.property.offer','property_type_id')
    offer_count = fields.Integer(compute="_compute_offer_count")

    _sql_constraints = [
        ('check_name_uniq', 'unique(name)', "Name already exists!"),
    ]

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for type in self:
            self.offer_count = len(type.mapped('offer_ids'))
