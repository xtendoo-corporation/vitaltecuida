from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_reward_wizard(self):
        """
        Intercepta la apertura del wizard de recompensas para validar restricciones de ewallet
        """
        # Validar restricciones de ewallet antes de abrir el wizard
        claimable_rewards = self._get_claimable_rewards()
        for coupon, rewards in claimable_rewards.items():
            for reward in rewards:
                program = reward.program_id
                if program and hasattr(program, 'electronic_monetary_product_id') and program.electronic_monetary_product_id:
                    program._validate_ewallet_usage(self.order_line)

        return super().action_open_reward_wizard()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _compute_price_reduce_taxinc(self):
        """
        Validar antes de aplicar descuentos de loyalty program
        """
        # Verificar si hay programas de loyalty con restricciones
        for line in self:
            if line.reward_id and line.reward_id.program_id.electronic_monetary_product_id:
                line.reward_id.program_id._validate_ewallet_usage(line.order_id.order_line)

        return super()._compute_price_reduce_taxinc()
