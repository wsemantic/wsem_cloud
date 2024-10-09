from odoo import http
from odoo.http import request
from odoo.service import db
from odoo import api, SUPERUSER_ID
import odoo
import ovh
import logging
import re
import configparser
import os

_logger = logging.getLogger(__name__)

class CustomSignupController(http.Controller):

    @http.route('/signup_step1', type='http', auth='public', website=True, csrf=True, lang='es_ES')
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
            subdomain = kwargs.get('subdomain')

            # Validar campos obligatorios
            if not all([name, email, company_name, dni, address, phone, subdomain]):
                error = 'Todos los campos son obligatorios.'
                return request.render('cloud_crm.signup_step1', {
                    'error': error,
                    'name': name,
                    'email': email,
                    'company_name': company_name,
                    'dni': dni,
                    'address': address,
                    'phone': phone,
                    'subdomain': subdomain,
                })

            # Generar el cloud_url
            cloud_url = f"{subdomain}.factuoo.com"
            
            # Verificar si existe un res.partner con el mismo cloud_url
            if self.url_exists(cloud_url):
                error_subdomain = 'La URL de la base de datos ya está en uso. Por favor modifica el subdominio o primera parte de la URL de tu base de datos.'
                return request.render('cloud_crm.signup_step1', {
                    'error_subdomain': error_subdomain,
                    'name': name,
                    'email': email,
                    'company_name': company_name,
                    'dni': dni,
                    'address': address,
                    'phone': phone,
                    'subdomain': subdomain,
                })

            # Buscar si existe un res.partner con el mismo email
            partner = self.find_partner_by_email(email)
            if partner:
                # Si el partner existe, actualizar su cloud_url
                try:
                    partner.sudo().write({
                        'name': name,
                        'company_name': company_name,
                        'vat': dni,
                        'street': address,
                        'phone': phone,
                        'cloud_url': cloud_url,
                    })
                except Exception as e:
                    _logger.error(f"Error al actualizar el res.partner: {e}")
                    error = 'Hubo un error al actualizar tu información. Por favor, inténtalo de nuevo.'
                    return request.render('cloud_crm.signup_step1', {
                        'error': error,
                        'name': name,
                        'email': email,
                        'company_name': company_name,
                        'dni': dni,
                        'address': address,
                        'phone': phone,
                        'subdomain': subdomain,
                    })
            else:
                # Si no existe, crear un nuevo res.partner
                try:
                    self.create_partner_in_db(name, email, company_name, dni, address, phone, cloud_url)
                except Exception as e:
                    _logger.error(f"Error al crear el res.partner: {e}")
                    error = 'Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo.'
                    return request.render('cloud_crm.signup_step1', {
                        'error': error,
                        'name': name,
                        'email': email,
                        'company_name': company_name,
                        'dni': dni,
                        'address': address,
                        'phone': phone,
                        'subdomain': subdomain,
                    })

            # Guardar los datos en la sesión
            request.session['signup_data'] = {
                'name': name,
                'email': email,
                'company_name': company_name,
                'dni': dni,
                'address': address,
                'phone': phone,
                'subdomain': subdomain,
                'cloud_url': cloud_url,
            }

            # Redirigir al segundo paso
            return request.redirect('/signup_step2')

        else:
            # Renderizar el formulario del primer paso
            return request.render('cloud_crm.signup_step1')

    @http.route('/signup_step2', type='http', auth='public', website=True, csrf=True, lang='es_ES')
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

            # Clonar la base de datos y crear el usuario
            try:
                self.create_user_and_db(signup_data, selected_modules)
            except Exception as e:
                _logger.error(f"Error al crear la base de datos y el usuario: {e}")
                return request.render('cloud_crm.signup_error', {'error': 'Hubo un error al crear la base de datos. Por favor, inténtalo de nuevo.'})

            # Limpiar la sesión
            request.session.pop('signup_data', None)

            # Redirigir a la página de éxito
            subdomain = signup_data.get('subdomain')
            db_url = f"https://{subdomain}.factuoo.com/web/login"
            return request.render('cloud_crm.signup_success_page', {
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

            return request.render('cloud_crm.signup_step2', {'modules': modules})
            # Renderizar el formulario del segundo paso con esta lista fija de módulos

    def create_user_and_db(self, signup_data, selected_modules):
        """
        Clona la base de datos, crea el usuario, instala los módulos seleccionados y crea el subdominio.
        """
        name = signup_data.get('name')
        email = signup_data.get('email')
        subdomain = signup_data.get('subdomain')

        target_db = subdomain  # Usamos el subdominio como nombre de la base de datos
        source_db = 'verifactu'  # Nombre de la base de datos predefinida a clonar

        _logger.info(f"Clonando la base de datos '{source_db}' a '{target_db}'")

        # Clonar la base de datos
        try:
            db.exp_duplicate_database(source_db, target_db, neutralize_database=False)
            _logger.info(f"Base de datos '{source_db}' clonada exitosamente como '{target_db}'")
        except Exception as e:
            _logger.error(f"Error al clonar la base de datos: {e}")
            raise

        # Instalar los módulos seleccionados en la nueva base de datos
        try:
            self.install_modules_in_db(target_db, selected_modules)
            _logger.info(f"Módulos {selected_modules} instalados en la base de datos '{target_db}'")
        except Exception as e:
            _logger.error(f"Error al instalar los módulos en la base de datos '{target_db}': {e}")
            raise

        # Crear el usuario en la nueva base de datos
        try:
            self.create_user_in_db(target_db, email, name)
            _logger.info(f"Usuario '{email}' creado en la base de datos '{target_db}'")
        except Exception as e:
            _logger.error(f"Error al crear el usuario en la base de datos '{target_db}': {e}")
            raise

        # Crear el subdominio en OVH
        try:
            self.create_subdomain_in_ovh(subdomain)
            _logger.info(f"Subdominio '{subdomain}.factuoo.com' creado en OVH")
        except Exception as e:
            _logger.error(f"Error al crear el subdominio '{subdomain}.factuoo.com' en OVH: {e}")
            raise
            
    def find_partner_by_email(self, email):
        """
        Busca un res.partner por email en la base de datos actual.
        """
        env = request.env
        partner = env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        return partner
        
    def url_exists(self, cloud_url):
        """
        Verifica si existe un res.partner con el mismo cloud_url.
        """
        env = request.env
        partner = env['res.partner'].sudo().search([('cloud_url', '=', cloud_url)], limit=1)
        return bool(partner)

    def create_partner_in_db(self, name, email, company_name, dni, address, phone, cloud_url):
        """
        Crea un res.partner en la base de datos actual con los datos proporcionados.
        """
        env = request.env
        partner_vals = {
            'name': name,
            'email': email,
            'company_name': company_name,
            'vat': dni,
            'street': address,
            'phone': phone,
            'cloud_url': cloud_url,
        }
        env['res.partner'].sudo().create(partner_vals)

    def create_subdomain_in_ovh(self, subdomain):
            """
            Crea el subdominio en OVH usando la API, leyendo las claves desde un archivo de configuración.
            """
            config_file = '/etc/letsencrypt/ovh.ini'  # Asegúrate de que esta ruta es correcta

            config = configparser.ConfigParser()
            _logger.info(f"Intentando leer el archivo de configuración: {config_file}")
            if not config.read(config_file):
                _logger.error(f"No se pudo leer el archivo de configuración: {config_file}")
                raise Exception("Archivo de configuración de OVH no encontrado o inaccesible.")

            if 'ovh_api' not in config.sections():
                _logger.error("No section: 'ovh_api' en el archivo de configuración.")
                raise Exception("Sección 'ovh_api' no encontrada en el archivo de configuración.")

            try:
                endpoint = config.get('ovh_api', 'endpoint')
                application_key = config.get('ovh_api', 'application_key')
                application_secret = config.get('ovh_api', 'application_secret')
                consumer_key = config.get('ovh_api', 'consumer_key')
                _logger.info("Configuración de OVH leída correctamente.")
            except configparser.NoOptionError as e:
                _logger.error(f"Falta la opción en la configuración: {e}")
                raise Exception(f"Opción faltante en la configuración: {e}")

            client = ovh.Client(
                endpoint=endpoint,
                application_key=application_key,
                application_secret=application_secret,
                consumer_key=consumer_key,
            )

            domain = "factuoo.com"
            ip_servidor_odoo = "79.143.93.12"  # Reemplaza con la IP real de tu servidor Odoo

            try:
                _logger.info(f"Creando registro A para el subdominio '{subdomain}.{domain}' apuntando a {ip_servidor_odoo}")
                response = client.post(
                    f"/domain/zone/{domain}/record",
                    fieldType="A",
                    subDomain=subdomain,
                    target=ip_servidor_odoo,
                    ttl=3600
                )
                client.post(f"/domain/zone/{domain}/refresh")
                _logger.info(f"Subdominio '{subdomain}.{domain}' creado exitosamente en OVH apuntando a {ip_servidor_odoo}.")
            except ovh.exceptions.APIError as e:
                _logger.error(f"Error al crear el subdominio en OVH: {e}")
                raise

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
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            user_obj = env['res.users']
            
            # Crear el nuevo usuario con un contexto que fuerce el envío del correo
            ctx = {
                'create_user': True,
                'no_reset_password': False,  # Asegura que se llame a action_reset_password
                'force_send': True,  # Fuerza el envío inmediato del correo
                'import_file': False,  # Asegura que force_send no se desactive
            }
            
            new_user = user_obj.with_context(ctx).create({
                'name': name,
                'login': email,
                'email': email,
                'notification_type': 'email',
            })
            
            # Forzar explícitamente el envío del correo de restablecimiento
            try:
                new_user.with_context(ctx).action_reset_password()
                _logger.info(f"WSEM Correo de restablecimiento enviado para el usuario {new_user.name} ({new_user.email})")
            except Exception as e:
                _logger.error(f"WSEM Error al enviar el correo de restablecimiento: {str(e)}")
            
            cr.commit()
            
        return new_user.id