from odoo import http
from odoo.http import request
from odoo.service import db
from odoo import api, SUPERUSER_ID
import odoo
import ovh
import logging
import re

_logger = logging.getLogger(__name__)

class CustomSignupController(http.Controller):

    @http.route('/signup_step1', type='http', auth='public', website=True, csrf=True)
    def signup_step1(self, **kwargs):
        """
        Maneja el primer paso del registro de usuario.
        """
        if request.httprequest.method == 'POST':
            # Capturar y validar los datos del formulario
            name = kwargs.get('name')
            email = kwargs.get('email')
            company_name = kwargs.get('company_name')
            dni = kwargs.get('dni')
            address = kwargs.get('address')
            phone = kwargs.get('phone')

            # Validar campos obligatorios
            if not all([name, email, company_name, dni, address, phone]):
                return request.render('wsem_cloud.signup_error', {'error': 'Todos los campos son obligatorios.'})

            # Guardar los datos en la sesión
            request.session['signup_data'] = {
                'name': name,
                'email': email,
                'company_name': company_name,
                'dni': dni,
                'address': address,
                'phone': phone,
            }

            # Redirigir al segundo paso
            return request.redirect('/signup_step2')

        else:
            # Renderizar el formulario del primer paso
            return request.render('wsem_cloud.auth_signup_step1')

    @http.route('/signup_step2', type='http', auth='public', website=True, csrf=True)
    def signup_step2(self, **kwargs):
        """
        Maneja el segundo paso del registro de usuario.
        """
        if request.httprequest.method == 'POST':
            # Obtener los módulos seleccionados
            selected_modules = request.httprequest.form.getlist('modules')
            signup_data = request.session.get('signup_data')

            if not signup_data:
                return request.redirect('/signup_step1')

            # Agregar el subdominio a los datos de registro
            company_name = signup_data.get('company_name')
            subdomain = self.generate_subdomain(company_name)
            if not subdomain:
                return request.render('wsem_cloud.signup_error', {'error': 'El subdominio generado no es válido.'})

            signup_data['subdomain'] = subdomain

            # Clonar la base de datos y crear el usuario
            try:
                self.create_user_and_db(signup_data, selected_modules)
            except Exception as e:
                _logger.error(f"Error al crear la base de datos y el usuario: {e}")
                return request.render('wsem_cloud.signup_error', {'error': 'Hubo un error al crear la base de datos. Por favor, inténtalo de nuevo.'})

            # Limpiar la sesión
            request.session.pop('signup_data', None)

            # Redirigir a la página de éxito
            db_url = f"https://{subdomain}.factuoo.com/web/login"
            return request.render('wsem_cloud.signup_success_page', {
                'email': signup_data.get('email'),
                'subdomain': subdomain,
                'db_url': db_url
            })

        else:
            # Definir una lista fija de módulos específicos
            modules = [
                {'name': 'Ventas', 'technical_name': 'sale_management', 'icon': '/path/to/sale_icon.png'},
                {'name': 'Contabilidad', 'technical_name': 'account', 'icon': '/path/to/account_icon.png'},
                {'name': 'Inventario', 'technical_name': 'stock', 'icon': '/path/to/stock_icon.png'},
                {'name': 'Compras', 'technical_name': 'purchase', 'icon': '/path/to/purchase_icon.png'}
            ]

            # Renderizar el formulario del segundo paso con esta lista fija de módulos
            return request.render('wsem_cloud.signup_step1', {'modules': modules})

    def create_user_and_db(self, signup_data, selected_modules):
        """
        Clona la base de datos, crea el usuario, instala los módulos seleccionados y crea el subdominio.
        """
        name = signup_data.get('name')
        email = signup_data.get('email')
        company_name = signup_data.get('company_name')
        subdomain = signup_data.get('subdomain')

        target_db = subdomain  # Usamos el subdominio como nombre de la base de datos
        source_db = 'base_predefinida'  # Nombre de la base de datos predefinida a clonar
        master_password = request.env['ir.config_parameter'].sudo().get_param('admin_passwd')

        # Clonar la base de datos
        try:
            db.duplicate_database(master_password, source_db, target_db)
            _logger.info(f"Base de datos '{source_db}' clonada como '{target_db}'.")
        except Exception as e:
            _logger.error(f"Error al clonar la base de datos: {e}")
            raise

        # Instalar los módulos seleccionados en la nueva base de datos
        try:
            self.install_modules_in_db(target_db, selected_modules)
            _logger.info(f"Módulos {selected_modules} instalados en la base de datos '{target_db}'.")
        except Exception as e:
            _logger.error(f"Error al instalar los módulos en la base de datos '{target_db}': {e}")
            raise

        # Crear el usuario en la nueva base de datos
        try:
            self.create_user_in_db(target_db, email, name)
            _logger.info(f"Usuario '{email}' creado en la base de datos '{target_db}'.")
        except Exception as e:
            _logger.error(f"Error al crear el usuario en la base de datos '{target_db}': {e}")
            raise

        # Crear el subdominio en OVH
        try:
            self.create_subdomain_in_ovh(subdomain)
            _logger.info(f"Subdominio '{subdomain}.factuoo.com' creado en OVH.")
        except Exception as e:
            _logger.error(f"Error al crear el subdominio '{subdomain}.factuoo.com' en OVH: {e}")
            raise

    def generate_subdomain(self, company_name):
        """
        Genera un subdominio válido basado en el nombre de la empresa.
        """
        # Eliminar espacios, caracteres especiales y convertir a minúsculas
        subdomain = re.sub(r'[^a-zA-Z0-9\-]', '', company_name.replace(' ', '').lower())
        # Eliminar guiones al inicio o final
        subdomain = subdomain.strip('-')
        return subdomain if subdomain else None

    def install_modules_in_db(self, db_name, modules_list):
        """
        Instala los módulos seleccionados en la base de datos clonada.
        """
        if not modules_list:
            return  # No hay módulos para instalar

        # Cambiar el contexto a la nueva base de datos
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            # Instalar los módulos
            module_obj = env['ir.module.module']
            modules_to_install = module_obj.search([('name', 'in', modules_list)])
            if modules_to_install:
                modules_to_install.button_immediate_install()

    def create_user_in_db(self, db_name, email, name):
        """
        Crea un usuario en la base de datos clonada y envía el correo para establecer contraseña.
        """
        # Cambiar el contexto a la nueva base de datos
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            user_obj = env['res.users']

            # Crear el nuevo usuario
            new_user = user_obj.create({
                'name': name,
                'login': email,
                'email': email,
                'notification_type': 'email',
            })

            # Enviar correo para establecer contraseña
            new_user.with_context(create_user=True).action_reset_password()

    def create_subdomain_in_ovh(self, subdomain):
        """
        Crea el subdominio en OVH usando la API.
        """
        client = ovh.Client(
            endpoint='ovh-eu',
            application_key='tu_application_key',
            application_secret='tu_application_secret',
            consumer_key='tu_consumer_key',
        )

        domain = "factuoo.com"

        # Crear un nuevo registro DNS tipo A
        try:
            response = client.post(
                f"/domain/zone/{domain}/record",
                fieldType="A",
                subDomain=subdomain,
                target="IP_DEL_SERVIDOR",
                ttl=3600
            )

            # Aplicar los cambios
            client.post(f"/domain/zone/{domain}/refresh")

        except ovh.exceptions.APIError as e:
            _logger.error(f"Error al crear el subdominio en OVH: {e}")
            raise

