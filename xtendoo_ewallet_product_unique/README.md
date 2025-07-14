# Xtendoo EWallet

## Descripción

Este módulo extiende el modelo `loyalty.program` de Odoo para añadir una relación con un producto específico que será el único que se puede pagar con el monedero electrónico (ewallet).

## Funcionalidades

- Añade el campo `electronic_monetary_product_id` al modelo `loyalty.program`
- Permite seleccionar un producto específico que puede ser pagado con el monedero electrónico
- Integra el campo en las vistas de formulario y lista del programa de lealtad

## Instalación

1. Asegúrate de que el módulo esté en la ruta de addons de Odoo
2. Actualiza la lista de aplicaciones
3. Instala el módulo "Xtendoo EWallet"

## Uso

1. Ve a Ventas > Configuración > Programas de Lealtad
2. Crea o edita un programa de lealtad
3. En el campo "Producto Monedero Electrónico", selecciona el producto que podrá ser pagado con este monedero
4. Guarda los cambios

## Dependencias

- base
- loyalty
- product

## Autor

Xtendoo - https://www.xtendoo.es
