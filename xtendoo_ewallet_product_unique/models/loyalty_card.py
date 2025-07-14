from odoo import models, api


class LoyaltyCard(models.Model):
    _inherit = 'loyalty.card'

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, **kwargs):
        """
        Interceptar search para filtrar automáticamente en contexto POS
        """
        # SIEMPRE aplicar filtro en búsquedas de loyalty cards para evitar problemas de caché
        # Solo si no hay ya un filtro de points en el dominio
        has_points_filter = any('points' in str(condition) for condition in domain if isinstance(condition, (list, tuple)))

        if not has_points_filter:
            domain = domain + [('points', '>', 0)]

        result = super().search(domain, offset=offset, limit=limit, order=order, **kwargs)

        # Si es una búsqueda de conteo, devolver directamente
        if kwargs.get('count', False):
            return result

        return result

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **kwargs):
        """
        Interceptar search_read para filtrar automáticamente en contexto POS
        """
        if domain is None:
            domain = []

        # SIEMPRE aplicar filtro si no hay filtro de points existente
        # Esto cubre tanto contexto POS como búsquedas específicas por partner+program
        has_points_filter = any('points' in str(condition) for condition in domain if isinstance(condition, (list, tuple)))

        if not has_points_filter:
            domain = domain + [('points', '>', 0)]

        result = super().search_read(domain, fields, offset, limit, order, **kwargs)

        return result

    def read(self, fields=None, load='_classic_read'):
        """
        Interceptar read para filtrar loyalty cards sin saldo en contexto POS
        """
        result = super().read(fields, load)

        # Detectar contexto POS de manera más amplia
        context_str = str(self.env.context)
        is_pos_context = (
            self.env.context.get('pos_session_id') or
            'pos' in context_str.lower() or
            'point_of_sale' in context_str.lower() or
            self.env.context.get('from_pos') or
            hasattr(self.env, 'pos') or
            'pos_' in context_str
        )

        if is_pos_context:
            # Filtrar solo tarjetas con points > 0
            filtered_result = []
            for card_data in result:
                if isinstance(card_data, dict) and card_data.get('points', 0) > 0:
                    filtered_result.append(card_data)

            return filtered_result

        return result

    def _consume_code(self, order, points_to_consume):
        """
        Intercepta el consumo de puntos/saldo del monedero para validar restricciones
        """
        # Validar restricciones de ewallet antes de consumir puntos
        if self.program_id.electronic_monetary_product_id:
            # Obtener líneas del pedido según el tipo de orden
            if hasattr(order, 'order_line'):  # Sale Order
                order_lines = order.order_line
            elif hasattr(order, 'lines'):  # POS Order
                order_lines = order.lines
            else:
                order_lines = []

            self.program_id._validate_ewallet_usage(order_lines)

        return super()._consume_code(order, points_to_consume)


class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'

    def _apply_reward(self, order, coupon_id=False):
        """
        Intercepta la aplicación de recompensas para validar restricciones de ewallet
        """
        # Validar restricciones de ewallet antes de aplicar la recompensa
        if self.program_id.electronic_monetary_product_id:
            # Obtener líneas del pedido según el tipo de orden
            if hasattr(order, 'order_line'):  # Sale Order
                order_lines = order.order_line
            elif hasattr(order, 'lines'):  # POS Order
                order_lines = order.lines
            else:
                order_lines = []

            self.program_id._validate_ewallet_usage(order_lines)

        return super()._apply_reward(order, coupon_id)
