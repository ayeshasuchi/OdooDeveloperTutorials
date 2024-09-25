import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import models, fields,api
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    active = fields.Boolean(default=True)
    price = fields.Float(required=True)
    status = fields.Selection(selection=[('accepted','Accepted'),('refused','Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer("Validity (days)",default=7)
    date_deadline = fields.Date("Deadline",compute='_compute_date_deadline',inverse='_inverse_date_deadline')
    # For stat button:
    property_type_id = fields.Many2one('estate.property.type',related='property_id.property_type_id',string='Property Type',store=True)

    _sql_constraints = [
        ('check_price_positive', 'CHECK(price >= 0)','An offer price must be strictly positive')
    ]

    @api.depends('validity','create_date')
    def _compute_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = date+timedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            date_diff = offer.date_deadline-date
            offer.validity = date_diff.days

    def action_accepted(self):
        for offer in self:
            if 'accepted' in self.mapped("property_id.offer_ids.status"):
                raise UserError("Only one offer can be accepted for a given property!")
            self.write({'status':'accepted'})

            return self.mapped('property_id').write(
                {
                    'buyer_id' : self.partner_id.id,
                    'selling_price' :self.price,
                    'state':'offer_accepted',
                }
            )

    def action_refused(self):
        for offer in self:
            offer.status='refused'

    @api.model
    def create(self, vals_list):
        if vals_list.get('property_id') and vals_list.get('price'):
            prop = self.env['estate.property'].browse(vals_list['property_id'])
            if prop.offer_ids:
                maxPrice = max(prop.mapped("offer_ids.price"))
                if vals_list['price'] <= maxPrice:
                    raise UserError("The offer price must be grater than %.2f" % maxPrice)
            prop.state='offer_received'
        return super().create(vals_list)

