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
import time

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
            street = kwargs.get('street')
            street2 = kwargs.get('street2')
            zip_id = kwargs.get('zip_id')  # Capturar zip_id del formulario
            phone = kwargs.get('phone')
            subdomain = kwargs.get('subdomain')

            # Buscar información del código postal seleccionado
            if zip_id:
                zip_record = request.env['res.city.zip'].sudo().browse(int(zip_id))
                if zip_record.exists():
                    postal_code = zip_record.name
                    city = zip_record.city_id.name
                    state_id = zip_record.city_id.state_id.id
                else:
                    postal_code = ''
                    city = ''
                    state_id = None
            else:
                postal_code = kwargs.get('zip')
                city = kwargs.get('city')
                state_id = None

            # Validar campos obligatorios
            # Diccionario de campos con sus nombres y valores
            fields = {
                "name": name,
                "email": email,
                "company_name": company_name,
                "dni": dni,
                "street": street,
                "postal_code": postal_code,
                "zip_id": zip_id,
                "city": city,
                "phone": phone,
                "subdomain": subdomain,
            }

            # Lista para almacenar los nombres de los campos que faltan
            missing_fields = [field for field, value in fields.items() if not value]

            if missing_fields:
                # Construir el mensaje de error con los nombres de los campos que faltan
                error = f"Los siguientes campos son obligatorios: {', '.join(missing_fields)}."
                _logger.error(f"WSEM {error}")
                return request.render('cloud_crm.signup_step1', {
                    'error': error,
                    **fields  # Pasamos los valores para rellenar el formulario con los datos introducidos
                })


            # Generar el cloud_url
            cloud_url = f"{subdomain}.factuoo.com"

            # Verificar si existe un res.partner con el mismo cloud_url
            if self.url_conflict(cloud_url, email):
                error_subdomain = f"'{subdomain}' ya está en uso. Por favor modifícalo e intenta de nuevo."
                return request.render('cloud_crm.signup_step1', {
                    'error_subdomain': error_subdomain,
                    'name': name,
                    'email': email,
                    'company_name': company_name,
                    'dni': dni,
                    'street': street,
                    'street2': street2,
                    'zip_id': zip_id,
                    'zip': postal_code,
                    'city': city,
                    'phone': phone,
                    'subdomain': subdomain,
                })

            # Buscar si existe un res.partner con el mismo email
            partner = self.find_partner_by_email(email)
            partner_vals = {
                'name': name,
                'email': email,
                'company_name': company_name,
                'vat': dni,
                'street': street,
                'street2': street2,
                'zip': postal_code,
                'city': city,
                'phone': phone,
                'cloud_url': cloud_url,
                'state_id': state_id,
            }

            if partner:
                # Si el partner existe, actualizar su información
                try:
                    partner.sudo().write(partner_vals)
                except Exception as e:
                    _logger.error(f"Error al actualizar el res.partner: {e}")
                    error = 'Hubo un error al actualizar tu información. Por favor, inténtalo de nuevo.'
                    return request.render('cloud_crm.signup_step1', {
                        'error': error,
                        'name': name,
                        'email': email,
                        'company_name': company_name,
                        'dni': dni,
                        'street': street,
                        'street2': street2,
                        'zip_id': zip_id,
                        'zip': postal_code,
                        'city': city,
                        'phone': phone,
                        'subdomain': subdomain,
                    })
            else:
                # Si no existe, crear un nuevo res.partner
                try:
                    self.create_partner_in_db(**partner_vals)
                except Exception as e:
                    _logger.error(f"Error al crear el res.partner: {e}")
                    error = 'Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo.'
                    return request.render('cloud_crm.signup_step1', {
                        'error': error,
                        'name': name,
                        'email': email,
                        'company_name': company_name,
                        'dni': dni,
                        'street': street,
                        'street2': street2,
                        'zip_id': zip_id,
                        'zip': postal_code,
                        'city': city,
                        'phone': phone,
                        'subdomain': subdomain,
                    })

            # Guardar los datos en la sesión
            request.session['signup_data'] = partner_vals
            request.session['signup_data']['subdomain'] = subdomain
            request.session['signup_data']['cloud_url'] = cloud_url

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
                {'name': 'Inventario', 'technical_name': 'stock', 'icon': '/cloud_crm/static/src/img/stock.svg'},
                {'name': 'Proyectos', 'technical_name': 'project', 'icon': '/cloud_crm/static/src/img/project.svg'},
                {'name': 'Fabricación', 'technical_name': 'mrp', 'icon': '/cloud_crm/static/src/img/mrp.svg'},
                {'name': 'CRM/Oportunidades Cliente', 'technical_name': 'crm', 'icon': '/cloud_crm/static/src/img/crm.svg'},                  
                {'name': 'Email Marketing', 'technical_name': 'mass_mailing', 'icon': '/cloud_crm/static/src/img/mass_mailing.svg'},            
                {'name': 'Sitio WEB', 'technical_name': 'website', 'icon': '/cloud_crm/static/src/img/website.svg'},  
                {'name': 'eCommerce', 'technical_name': 'website_sale', 'icon': '/cloud_crm/static/src/img/website_sale.svg'},  
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
        company_name= signup_data.get('company_name')

        target_db = subdomain  # Usamos el subdominio como nombre de la base de datos
        source_db = 'verifactu'  # Nombre de la base de datos predefinida a clonar
        
        # Crear el subdominio en OVH
        try:
            self.create_subdomain_in_ovh(subdomain)
            _logger.info(f"Subdominio '{subdomain}.factuoo.com' creado en OVH")
        except Exception as e:
            _logger.error(f"Error al crear el subdominio '{subdomain}.factuoo.com' en OVH: {e}")
            raise

        _logger.info(f"WSEM Clonando la base de datos '{source_db}' a '{target_db}'")
        time.sleep(10)
        _logger.info(f"WSEM sleep")
        # Clonar la base de datos
        try:
            db.exp_duplicate_database(source_db, target_db, neutralize_database=False)
            _logger.info(f"WSEM Base de datos '{source_db}' clonada exitosamente como '{target_db}'")
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
            self.create_user_in_db(target_db, email, name, subdomain, company_name)
            _logger.info(f"WSEM Usuario '{email}' creado en la base de datos '{target_db}'")
        except Exception as e:
            _logger.error(f"Error al crear el usuario en la base de datos '{target_db}': {e}")
            raise
            
        # Limpiar el servidor de correo y el email de la compañía en la nueva base de datos
        try:
            self.clean_mail_server_and_company_email(target_db)
            _logger.info(f"Servidor de correo y email de la compañía limpiados en la base de datos '{target_db}'")
            self.activate_security_rules(target_db,['factuoo', 'cloud'])
            _logger.info(f"Activad reglas en '{target_db}'")
        except Exception as e:
            _logger.error(f"Error al limpiar el servidor de correo o el email de la compañía: {e}")
            raise
            
    def find_partner_by_email(self, email):
        """
        Busca un res.partner por email en la base de datos actual.
        """
        env = request.env
        partner = env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        return partner
        
    def url_conflict(self, cloud_url, email):
        """
        Verifica si existe un res.partner con el mismo cloud_url pero diferente email.
        """
        env = request.env
        # Buscar un partner que tenga el mismo cloud_url
        partner = env['res.partner'].sudo().search([('cloud_url', '=', cloud_url)], limit=1)
        
        # Verificar si el partner existe y si el email es diferente
        if partner and partner.email != email:
            return True
        return False


    def create_partner_in_db(self, name, email, company_name, dni, street, street2, postal_code, city, phone, cloud_url):
        """
        Crea un res.partner en la base de datos actual con los datos proporcionados.
        """
        env = request.env
        partner_vals = {
            'name': name,
            'email': email,
            'company_name': company_name,
            'vat': dni,
            'street': street,
            'street2': street2,
            'zip': postal_code,
            'city': city,
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

    def create_user_in_db(self, db_name, email, name, subdomain, company_name):
        registry = odoo.registry(db_name)
        #REQUISITOS
        # La base de datos a clonar debe incluir la configuración de correo (por ejemplo, factuoo)
        # El mail de la compañía se usará como remitente para el envío automático de la invitación, debe ser del mismo dominio que la base de datos (registro@factuoo.com)
        # Ambas configuraciones se limpian al final con el método clean
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Actualizar el nombre de la única compañía existente
            company = env['res.company'].search([], limit=1)
            if company:
                company.sudo().write({'name': company_name})
                _logger.info(f"Nombre de la compañía actualizado a: {company_name}")
            else:
                raise UserError("No se encontró ninguna compañía en la base de datos.")
                
            # Verificar y cargar la configuración del servidor de correo
            mail_server = env['ir.mail_server'].search([], limit=1)
            if not mail_server:
                raise UserError("No se encontró configuración de servidor de correo en la base de datos de destino.")
            
            _logger.info(f"Usando servidor de correo: {mail_server.name}")
            
            # Actualizar el parámetro `web.base.url` en la nueva base de datos
            base_url = f"https://{subdomain}.factuoo.com"
            env['ir.config_parameter'].sudo().set_param('web.base.url', base_url)
            _logger.info(f"Parámetro 'web.base.url' configurado como: {base_url}")
        
            # Crear el nuevo usuario
            user_obj = env['res.users']
            new_user = user_obj.create({
                'name': name,
                'login': email,
                'email': email,
                'notification_type': 'email',
            })
            
            # Asignar el usuario al grupo de administradores
            self.assign_admin_group(env, new_user)
            
            _logger.info(f"Usuario creado: {new_user.name} (ID: {new_user.id})")
           
            
            # Confirmar la transacción
            cr.commit()
    
    def assign_admin_group(self, env, user):
        """
        Asigna al usuario proporcionado al grupo de administradores.
        
        :param env: Entorno de Odoo.
        :param user: Registro del usuario a asignar.
        """
        try:
            # Obtener la referencia al grupo de administradores
            admin_group = env.ref('base.group_system')
        except ValueError:
            _logger.error("No se encontró el grupo 'Administration / Settings' (base.group_system).")
            raise UserError("No se pudo asignar al grupo de administradores porque no se encontró 'base.group_system'.")

        if admin_group:
            # Asignar el grupo al usuario
            user.groups_id = [(4, admin_group.id)]
            _logger.info(f"Usuario '{user.name}' asignado al grupo de administradores.")
        else:
            _logger.error("El grupo 'Administration / Settings' no está disponible en esta base de datos.")
            raise UserError("No se pudo asignar al grupo de administradores porque no está disponible.")


    def activate_security_rules(self, db_name, keywords):
        """
        Método para activar reglas de seguridad basadas en palabras clave.
        
        :param db_name: Nombre de la base de datos.
        :param keywords: Lista de palabras clave para buscar en el nombre de las reglas.
        """        
        # Construir dominio de búsqueda dinámicamente
        if len(keywords) > 1:
            # Añadir N-1 operadores '|'
            domain = ['|'] * (len(keywords) - 1) + [('name', 'ilike', kw) for kw in keywords]
        else:
            domain = [('name', 'ilike', keywords[0])]
        
        _logger.info(f"Dominio de búsqueda construido: {domain}")
        
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
            # Buscar las reglas que coinciden con las palabras clave
            rules = env['ir.rule'].search(domain)
            
            # Log de las reglas encontradas
            if rules:
                rule_names = rules.mapped('name')
                _logger.info(f"Reglas encontradas para {keywords}: {rule_names}")
                # Activar las reglas encontradas
                rules.write({'active': True})
                _logger.info(f"Activadas {len(rules)} reglas de seguridad relacionadas con {keywords}.")
            else:
                _logger.warning(f"No se encontraron reglas de seguridad con las palabras clave: {keywords}.")
                # Opcional: Listar todas las reglas para depuración
                all_rules = env['ir.rule'].search([])
                all_rule_names = all_rules.mapped('name')
                _logger.debug(f"Todas las reglas de seguridad disponibles: {all_rule_names}")

            
    def clean_mail_server_and_company_email(self, db_name):
        """
        Elimina la configuración de servidor de correo y limpia el email de la compañía.
        """
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Limpiar el servidor de correo saliente
            mail_server = env['ir.mail_server'].search([], limit=1)
            if mail_server:
                mail_server.sudo().unlink()
                _logger.info(f"Servidor de correo eliminado en la base de datos '{db_name}'")

            # Limpiar el email de la compañía
            company = env['res.company'].search([], limit=1)
            if company:
                company.sudo().write({'email': False})
                _logger.info(f"Email de la compañía eliminado en la base de datos '{db_name}'")
                
            

            cr.commit()            
            