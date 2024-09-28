from odoo import models, fields, _, Command
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        res = super(EstateProperty, self).action_sold()
        #create invoice
        self.ensure_one()
        #journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        invoice_vals_list = {
            'move_type': 'out_invoice',
            'partner_id': self.buyer_id.id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_line_ids':[
                Command.create({
                        'name':self.name,
                        'quantity':1.00,
                        'price_unit': self.selling_price*6.00/100.00,
                    }
                )
                ,Command.create(
                    {
                        'name':'Administrative Fees',
                        'quantity':1.00,
                        'price_unit': 100.00,
                    }
                )
            ]
        }
        moves = (self.env['account.move'].sudo().with_context(default_move_type='out_invoice')
                 .create(invoice_vals_list))


        return res
