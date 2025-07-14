from odoo import models, api, _
from odoo.exceptions import ValidationError, UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _apply_program_reward(self, program, coupon_id=False):
        """
        Intercepta la aplicación de recompensas de loyalty program en POS para validar restricciones de ewallet
        """
        # Validar restricciones de ewallet antes de aplicar la recompensa
        if program.electronic_monetary_product_id:
            try:
                program._validate_ewallet_usage(self.lines)
            except ValidationError as e:
                # Convertir ValidationError a UserError para mejor manejo en POS
                raise UserError(e.args[0])

        return super()._apply_program_reward(program, coupon_id)

    def _process_saved_order(self, draft):
        """
        Validar restricciones al procesar órdenes guardadas
        """
        # Verificar restricciones de ewallet en líneas de loyalty
        for line in self.lines:
            if line.reward_id and line.reward_id.program_id.electronic_monetary_product_id:
                line.reward_id.program_id._validate_ewallet_usage(self.lines)

        return super()._process_saved_order(draft)


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.model
    def create(self, vals):
        """
        Validar al crear líneas de POS que contengan rewards de ewallet
        """
        result = super().create(vals)

        # Si la línea es una recompensa de loyalty program con restricciones
        if result.reward_id and result.reward_id.program_id.electronic_monetary_product_id:
            result.reward_id.program_id._validate_ewallet_usage(result.order_id.lines)

        return result
