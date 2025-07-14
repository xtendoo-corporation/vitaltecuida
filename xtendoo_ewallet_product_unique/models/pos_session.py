from odoo import models, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    def load_data(self, data=None):
        """
        Interceptar la carga de datos del POS para filtrar loyalty cards
        """
        # Cargar datos normalmente
        result = super().load_data(data)

        # Verificar si hay datos de loyalty cards
        if 'loyalty.card' in result:
            original_cards = result['loyalty.card']

            # Si tiene la estructura {'data': [...], 'fields': [...], 'relations': [...]}
            if isinstance(original_cards, dict) and 'data' in original_cards:
                cards_list = original_cards['data']
                filtered_cards_list = []

                for card in cards_list:
                    if isinstance(card, dict):
                        points = card.get('points', 0)
                        if points > 0:
                            filtered_cards_list.append(card)

                # Actualizar con datos filtrados
                filtered_cards = {
                    'data': filtered_cards_list,
                    'fields': original_cards.get('fields', []),
                    'relations': original_cards.get('relations', [])
                }
                result['loyalty.card'] = filtered_cards

        return result

    def _loader_params_loyalty_card(self):
        """
        Modificar parámetros de carga de loyalty cards para filtrar solo las activas
        """
        result = super()._loader_params_loyalty_card()

        # Agregar filtro para solo cargar tarjetas con saldo > 0
        if 'search_params' in result:
            if 'domain' not in result['search_params']:
                result['search_params']['domain'] = []
            result['search_params']['domain'].append(('points', '>', 0))
        else:
            result['search_params'] = {
                'domain': [('points', '>', 0)]
            }

        return result

    def _pos_ui_models_to_load(self):
        """
        Asegurar que se carguen los modelos necesarios
        """
        result = super()._pos_ui_models_to_load()
        return result

    def _get_pos_ui_loyalty_card(self, params):
        """
        Filtrar loyalty cards para mostrar solo las activas en POS
        """
        domain = params.get('domain', [])
        # Agregar filtro para solo mostrar tarjetas con puntos > 0
        domain.append(('points', '>', 0))

        fields = params.get('fields', [])

        # Buscar solo tarjetas activas
        loyalty_cards = self.env['loyalty.card'].search(domain)
        return loyalty_cards.read(fields)
