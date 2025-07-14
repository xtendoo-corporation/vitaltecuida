from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    electronic_monetary_product_id = fields.Many2one(
        'product.product',
        string='Producto Monedero Electrónico',
        help='Producto único que se puede pagar con este monedero electrónico'
    )

    def _check_ewallet_product_restriction(self, order_lines):
        """
        Verifica si se puede usar el monedero electrónico basado en los productos del pedido.
        Solo se permite si el único producto es el configurado en electronic_monetary_product_id.
        """
        if not self.electronic_monetary_product_id:
            return True  # Si no hay restricción configurada, permitir uso normal

        # Obtener productos únicos de las líneas del pedido (excluyendo servicios de loyalty y monederos electrónicos)
        products_in_order = set()

        for line in order_lines:
            if hasattr(line, 'product_id') and line.product_id:
                # Excluir productos de loyalty/rewards y monederos electrónicos
                product_type = getattr(line.product_id, 'detailed_type', None) or getattr(line.product_id, 'type', 'consu')
                product_name = (line.product_id.name or '').lower()

                # Incluir solo productos que NO sean de loyalty ni monederos electrónicos
                is_loyalty_product = (product_type == 'service' and 'loyalty' in product_name)
                is_ewallet_product = ('monedero' in product_name or 'ewallet' in product_name or 'wallet' in product_name)

                if not is_loyalty_product and not is_ewallet_product:
                    products_in_order.add(line.product_id.id)

        # Validación final
        is_valid = len(products_in_order) == 1 and self.electronic_monetary_product_id.id in products_in_order

        # Si hay más de un producto o el producto no es el permitido
        if len(products_in_order) != 1 or self.electronic_monetary_product_id.id not in products_in_order:
            return False

        return True

    def _validate_ewallet_usage(self, order_lines):
        """
        Valida que se pueda usar el monedero electrónico y lanza excepción si no es válido.
        """
        if not self._check_ewallet_product_restriction(order_lines):
            # Obtener información adicional para el mensaje de error
            products_info = []
            for line in order_lines:
                if hasattr(line, 'product_id') and line.product_id:
                    qty = getattr(line, 'qty', getattr(line, 'product_uom_qty', 1))
                    products_info.append(f"- {line.product_id.name} (ID: {line.product_id.id}, Qty: {qty})")

            products_list = "\n".join(products_info)

            raise ValidationError(_(
                'El monedero electrónico "%s" solo puede ser usado cuando el único producto '
                'en el pedido sea "%s".\n\nProductos actuales en el pedido:\n%s'
            ) % (self.name, self.electronic_monetary_product_id.name, products_list))

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **kwargs):
        """
        Interceptar search_read para filtrar programas en contexto POS
        """
        result = super().search_read(domain, fields, offset, limit, order, **kwargs)

        # Si estamos en contexto POS, filtrar programas sin tarjetas activas
        if self.env.context.get('pos_session_id') or 'pos' in str(self.env.context):
            filtered_result = []
            for program_data in result:
                program_id = program_data.get('id')

                # Verificar si este programa tiene tarjetas activas
                active_cards_count = self.env['loyalty.card'].search_count([
                    ('program_id', '=', program_id),
                    ('points', '>', 0)
                ])

                if active_cards_count > 0:
                    filtered_result.append(program_data)

            return filtered_result

        return result

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, **kwargs):
        """
        Interceptar search para filtrar programas en contexto POS
        """
        # Si estamos en contexto POS, filtrar programas sin tarjetas activas
        if self.env.context.get('pos_session_id') or 'pos' in str(self.env.context):
            # Obtener programas base
            programs = super().search(domain, offset=offset, limit=limit, order=order, **kwargs)

            # Si es una búsqueda de conteo, devolver directamente
            if kwargs.get('count', False):
                return programs

            # Filtrar solo programas con tarjetas activas
            active_programs = self.env['loyalty.program']
            for program in programs:
                active_cards_count = self.env['loyalty.card'].search_count([
                    ('program_id', '=', program.id),
                    ('points', '>', 0)
                ])

                if active_cards_count > 0:
                    active_programs |= program

            return active_programs

        return super().search(domain, offset=offset, limit=limit, order=order, **kwargs)
