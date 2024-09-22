from datetime import timedelta
from logging import exception

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "EstateProperty"
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.today() + timedelta(days=90))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted')
            , ('sold', 'Sold'), ('canceled', 'Canceled')], default='new', copy=False, required=True)
    property_type_id = fields.Many2one('estate.property.type')
    buyer_id = fields.Many2one("res.partner", copy=False)
    salesman_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    total_area = fields.Float(compute='_compute_total_area', string='Total Area (sqm)')
    best_price = fields.Float(compute='_compute_best_price')

    _sql_constraints = [
        ('check_expected_price_positive','CHECK(expected_price >= 0)','A property expected price must be strictly positive')
        ,('check_selling_price_positive','CHECK(selling_price >= 0)','A property selling price must be positive')
    ]

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for prop in self:
            prop.total_area = prop.living_area + prop.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for prop in self:
            print(prop.offer_ids)
            prop.best_price =  max(prop.offer_ids.mapped('price')) if prop.offer_ids else 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area=10
            self.garden_orientation= 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for prop in self:
            if prop.state == 'canceled':
                raise UserError("A canceled property cannot be set as sold.")
            prop.state='sold'

    def action_cancel(self):
        for prop in self:
            if prop.state == 'sold':
                raise UserError("A sold property cannot be canceled.")
            prop.state='canceled'

    @api.constrains('expected_price','selling_price')
    def check_price(self):
        for prop in self:
            if not float_is_zero(prop.selling_price,precision_rounding=0.01) and float_compare(prop.selling_price,prop.expected_price*0.9,precision_rounding=0.01) < 0:
                raise ValidationError("Selling price cannot be lower than 90% of the expected price.")

    @api.ondelete(at_uninstall=False)
    def _unlink_property(self):
        if self.state not in ('new','canceled') :
            raise UserError("Deletion of a property not possible for state is not ‘New’ or ‘Canceled’")
