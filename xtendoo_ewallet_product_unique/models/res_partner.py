from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_loyalty_card_ids_for_pos(self):
        """
        Método específico para obtener solo loyalty cards activas en POS
        """
        active_cards = self.env['loyalty.card'].search([
            ('partner_id', '=', self.id),
            ('points', '>', 0)
        ])
        return active_cards.ids

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **kwargs):
        """
        Interceptar search_read para modificar loyalty_card_ids en contexto POS
        """
        result = super().search_read(domain, fields, offset, limit, order, **kwargs)

        # Si estamos en contexto POS, filtrar loyalty cards
        context_str = str(self.env.context)
        is_pos_context = ('pos' in context_str or self.env.context.get('pos_session_id'))

        if is_pos_context:
            for partner_data in result:
                if isinstance(partner_data, dict) and partner_data.get('id'):
                    # Obtener partner y sus loyalty cards activas
                    partner = self.browse(partner_data['id'])
                    active_card_ids = partner._get_loyalty_card_ids_for_pos()

                    # Reemplazar loyalty_card_ids con solo las activas
                    if 'loyalty_card_ids' in partner_data:
                        partner_data['loyalty_card_ids'] = active_card_ids

                    # También agregar un campo auxiliar para debugging
                    partner_data['active_loyalty_count'] = len(active_card_ids)

        return result

    def read(self, fields=None, load='_classic_read'):
        """
        Interceptar read para modificar loyalty_card_ids en contexto POS
        """
        result = super().read(fields, load)

        # Si estamos en contexto POS, filtrar loyalty cards
        context_str = str(self.env.context)
        is_pos_context = ('pos' in context_str or self.env.context.get('pos_session_id'))

        if is_pos_context:
            for partner_data in result:
                if isinstance(partner_data, dict) and partner_data.get('id'):
                    # Obtener partner y sus loyalty cards activas
                    partner = self.browse(partner_data['id'])
                    active_card_ids = partner._get_loyalty_card_ids_for_pos()

                    # Reemplazar loyalty_card_ids con solo las activas
                    if 'loyalty_card_ids' in partner_data:
                        partner_data['loyalty_card_ids'] = active_card_ids

        return result

    # Sobrescribir directamente el campo loyalty_card_ids en contexto POS
    def _compute_loyalty_card_ids_pos(self):
        """
        Computar loyalty_card_ids filtradas para POS
        """
        for partner in self:
            if self.env.context.get('pos_session_id') or 'pos' in str(self.env.context):
                # En contexto POS, solo mostrar tarjetas activas
                active_cards = self.env['loyalty.card'].search([
                    ('partner_id', '=', partner.id),
                    ('points', '>', 0)
                ])
                partner.loyalty_card_ids_pos = active_cards
            else:
                # En otros contextos, mostrar todas
                partner.loyalty_card_ids_pos = partner.loyalty_card_ids

    loyalty_card_ids_pos = fields.One2many(
        'loyalty.card',
        'partner_id',
        compute='_compute_loyalty_card_ids_pos',
        string='Loyalty Cards (POS)',
        help='Loyalty cards filtradas para POS - solo activas'
    )
