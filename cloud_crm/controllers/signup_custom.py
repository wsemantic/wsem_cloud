from odoo import http
from odoo.http import request
from odoo.service import db
from odoo import api, SUPERUSER_ID
import odoo
from odoo.exceptions import UserError
from odoo.modules.registry import Registry
import ovh
import logging
import re
import configparser
import os
import time
import json
import socket

_logger = logging.getLogger(__name__)

class CustomSignupController(http.Controller):

    @http.route('/signup_step1', type='http', auth='public', website=True, csrf=True, lang='es_ES')
    def signup_step1(self, **kwargs):
        """
        Maneja el primer paso del registro de usuario.
        """
        if request.httprequest.method == 'POST':
            # Capturar y validar los datos del formulario
            name = (kwargs.get('name') or '').strip()
            email = (kwargs.get('email') or '').strip().lower()
            company_name = (kwargs.get('company_name') or '').strip()
            dni = (kwargs.get('dni') or '').strip().upper()
            street = (kwargs.get('street') or '').strip()
            street2 = (kwargs.get('street2') or '').strip()
            zip_id = (kwargs.get('zip_id') or '').strip()  # Capturar zip_id del formulario
            phone = (kwargs.get('phone') or '').strip()
            subdomain = (kwargs.get('subdomain') or '').strip()

            # Buscar información del código postal seleccionado
            if zip_id:
                if str(zip_id).isdigit():
                    zip_record = request.env['res.city.zip'].sudo().browse(int(zip_id))
                    if zip_record.exists():
                        postal_code = zip_record.name
                        city = zip_record.city_id.name
                        state_id = zip_record.city_id.state_id.id
                        _logger.info(f"WSEM ZIp exists {postal_code}")
                    else:
                        _logger.error("WSEM ZIp Not exists")
                        postal_code = ''
                        city = ''
                        state_id = None
                else:
                    error = "Código postal inválido."
                    _logger.error(f"WSEM invalid zip_id value {zip_id}")
                    return request.render('cloud_crm.signup_step1', {
                        'error': error,
                        'name': name,
                        'email': email,
                        'company_name': company_name,
                        'dni': dni,
                        'street': street,
                        'street2': street2,
                        'zip_id': '',
                        'zip': kwargs.get('zip'),
                        'city': kwargs.get('city'),
                        'phone': phone,
                        'subdomain': subdomain,
                    })
            else:
                postal_code = kwargs.get('zip')
                city = kwargs.get('city')
                state_id = None

            # Validar campos obligatorios
            # Diccionario de campos con sus nombres y valores
            required_fields = {
                "Nombre": name,
                "Correo electrónico": email,
            }

            # Lista para almacenar los nombres de los campos que faltan
            missing_fields = [field for field, value in required_fields.items() if not value]

            if missing_fields:
                # Construir el mensaje de error con los nombres de los campos que faltan
                error = f"Los siguientes campos son obligatorios: {', '.join(missing_fields)}."
                _logger.error(f"WSEM {error}")
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

            if dni and not re.match(r'^[A-Z]{2}', dni):
                dni = f'ES{dni}'
            if dni and not dni.startswith('ES'):
                error = "Solo se permiten NIF españoles (prefijo ES)."
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
            # Determinar el tipo de partner según el NIF
            partner = self.find_partner_by_email(email)
            company_type = partner.company_type if partner and partner.company_type else 'person'
            if dni:
                try:
                    company_type = self._get_company_type(dni)
                except ValueError as e:
                    error = str(e)
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

                if company_type == 'company' and not company_name:
                    error = "El campo Empresa es obligatorio para compañías."
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


            if not subdomain:
                if partner and partner.cloud_url:
                    subdomain = self._extract_subdomain_from_url(partner.cloud_url)
                if not subdomain:
                    subdomain = self._generate_subdomain(name, email)

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
                'company_type': company_type,
            }

            if partner:
                # Si el partner existe, actualizar su información
                try:
                    partner.sudo().with_context(no_vat_validation=True, lang='es_ES').write(partner_vals)
                except Exception as e:
                    _logger.exception(
                        "Error al actualizar el res.partner con email '%s'", email
                    )
                    error = getattr(e, 'name', str(e))
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
                    partner = self.create_partner_in_db(**partner_vals)
                except Exception as e:
                    _logger.exception(
                        "Error al crear el res.partner con email '%s'", email
                    )
                    error = getattr(e, 'name', str(e))
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
            session_vals = dict(partner_vals)
            session_vals.update({
                'subdomain': subdomain,
                'cloud_url': cloud_url,
                'partner_id': partner.id if partner else None,
            })
            request.session['signup_data'] = session_vals

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
                creation_result = self.create_user_and_db(signup_data, selected_modules)
            except Exception:
                _logger.exception(
                    "Error al crear la base de datos y el usuario para '%s'",
                    signup_data.get('email'),
                )
                return request.render(
                    'cloud_crm.signup_error',
                    {
                        'error': 'Hubo un error al crear la base de datos. Por favor, inténtalo de nuevo.'
                    },
                )

            # Limpiar la sesión
            request.session.pop('signup_data', None)

            # Redirigir a la página de éxito
            subdomain = signup_data.get('subdomain')
            creation_result = creation_result or {}
            db_url = creation_result.get('db_url') or f"https://{subdomain}.factuoo.com/odoo/login"
            return request.render('cloud_crm.signup_success_page', {
                'email': signup_data.get('email'),
                'name': signup_data.get('name'),
                'subdomain': subdomain,
                'db_url': db_url,
                'creation_status': creation_result.get('status', 'created'),
                'reuse_reason': creation_result.get('reason'),
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
        company_name = (signup_data.get('company_name') or '').strip()
        if not company_name:
            # Si el usuario no indicó empresa, usar el nombre del registro
            company_name = (name or '').strip()
        street = signup_data.get('street')
        street2 = signup_data.get('street2')
        zip_code = signup_data.get('zip')
        city = signup_data.get('city')
        state_id = signup_data.get('state_id')
        phone = signup_data.get('phone')

        partner = None
        partner_id = signup_data.get('partner_id')
        try:
            partner_id = int(partner_id)
        except (TypeError, ValueError):
            partner_id = False
        if partner_id:
            partner = request.env['res.partner'].sudo().browse(partner_id)
            if not partner.exists():
                partner = None
        if not partner and email:
            partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)

        existing_partner_cloud_url = ''
        existing_partner_subdomain = ''
        if partner and partner.cloud_url:
            existing_partner_cloud_url = partner.cloud_url or ''
            existing_partner_subdomain = self._extract_subdomain_from_url(existing_partner_cloud_url)

        target_db = subdomain  # Usamos el subdominio como nombre de la base de datos
        source_db = 'veri-template'  # Nombre de la base de datos predefinida a clonar

        if existing_partner_subdomain:
            if not subdomain:
                subdomain = existing_partner_subdomain
            if existing_partner_subdomain == subdomain:
                target_db = existing_partner_subdomain
                db_login_url = f"https://{target_db}.factuoo.com/odoo/login"
                if db.exp_db_exist(target_db):
                    _logger.info(
                        "El partner ya contaba con un entorno en '%s'. Se reutiliza la configuración existente.",
                        existing_partner_cloud_url,
                    )
                    return {
                        'status': 'reused',
                        'reason': 'existing_partner',
                        'db_url': db_login_url,
                    }
                _logger.warning(
                    "El partner tiene asignada la URL '%s' pero la base de datos '%s' no existe. Se volverá a aprovisionar.",
                    existing_partner_cloud_url,
                    existing_partner_subdomain,
                )

        db_login_url = f"https://{subdomain}.factuoo.com/odoo/login"

        if db.exp_db_exist(target_db):
            _logger.info(
                "La base de datos '%s' ya existe. Se reutiliza el entorno existente.",
                target_db,
            )
            return {
                'status': 'reused',
                'reason': 'database_exists',
                'db_url': db_login_url,
            }

        # Crear el subdominio en OVH
        should_create_subdomain = not (existing_partner_subdomain and existing_partner_subdomain == subdomain)
        if should_create_subdomain:
            try:
                self.create_subdomain_in_ovh(subdomain)
                _logger.info(f"Subdominio '{subdomain}.factuoo.com' creado en OVH")
            except Exception:
                _logger.exception(
                    "Error al crear el subdominio '%s.factuoo.com' en OVH", subdomain
                )
                raise
        else:
            _logger.info(
                "Se omite la creación del subdominio '%s.factuoo.com' porque ya estaba registrado para el partner.",
                subdomain,
            )

        _logger.info(f"WSEM Clonando la base de datos '{source_db}' a '{target_db}'")
        time.sleep(10)
        _logger.info(f"WSEM sleep")
        # Clonar la base de datos
        try:
            db.exp_duplicate_database(source_db, target_db, neutralize_database=False)
            _logger.info(
                f"WSEM Base de datos '{source_db}' clonada exitosamente como '{target_db}'"
            )
        except Exception:
            _logger.exception(
                "Error al clonar la base de datos '%s' hacia '%s'", source_db, target_db
            )
            raise

        # Instalar los módulos seleccionados en la nueva base de datos
        try:
            self.install_modules_in_db(target_db, selected_modules)
            _logger.info(
                f"Módulos {selected_modules} instalados en la base de datos '{target_db}'"
            )
        except Exception:
            _logger.exception(
                "Error al instalar los módulos en la base de datos '%s'", target_db
            )
            raise
            
        # Crear el usuario en la nueva base de datos
        try:
            self.create_user_in_db(
                target_db,
                email,
                name,
                subdomain,
                company_name,
                street,
                street2,
                zip_code,
                city,
                state_id,
                phone,
            )
            _logger.info(
                f"WSEM Usuario '{email}' creado en la base de datos '{target_db}'"
            )
        except Exception:
            _logger.exception(
                "Error al crear el usuario '%s' en la base de datos '%s'", email, target_db
            )
            raise
                    
        try:
            '''# Limpiar el servidor de correo y el email de la compañía en la nueva base de datos
            self.clean_mail_server(target_db)
            _logger.info(
                f"Servidor de correo y email de la compañía limpiados en la base de datos '{target_db}'"
            )'''
            self.activate_security_rules(target_db, ['factuoo', 'cloud'])
            _logger.info(f"Activad reglas en '{target_db}'")
        except Exception:
            _logger.exception(
                "Error al limpiar el servidor de correo o activar reglas en '%s'", target_db
            )
            raise

        return {
            'status': 'created',
            'reason': 'provisioned',
            'db_url': db_login_url,
        }
            
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

    def _sanitize_subdomain_candidate(self, value):
        value = (value or '').lower()
        # Reemplazar espacios y caracteres no válidos por '-'
        value = re.sub(r'[^a-z0-9-]+', '-', value)
        value = re.sub(r'-+', '-', value).strip('-')
        return value

    def _generate_subdomain(self, name, email):
        base_candidates = []
        if email and '@' in email:
            base_candidates.append(email.split('@')[0])
        base_candidates.extend([name, 'cliente'])

        base = ''
        for candidate in base_candidates:
            sanitized = self._sanitize_subdomain_candidate(candidate)
            if sanitized:
                base = sanitized
                break

        if not base:
            base = 'cliente'

        subdomain = base
        counter = 1
        while self.url_conflict(f"{subdomain}.factuoo.com", email):
            counter += 1
            subdomain = f"{base}-{counter}"

        return subdomain

    def _extract_subdomain_from_url(self, cloud_url):
        if not cloud_url:
            return ''

        cleaned = cloud_url
        if '://' in cleaned:
            cleaned = cleaned.split('://', 1)[1]

        cleaned = cleaned.split('/')[0]

        if cleaned.endswith('.factuoo.com'):
            cleaned = cleaned[: -len('.factuoo.com')]

        return self._sanitize_subdomain_candidate(cleaned)

    def _get_company_type(self, vat):
        """Devuelve 'person' o 'company' según el formato del NIF.

        Acepta NIF de individuos (00000000A) y CIF de empresas (A00000000).
        Lanza ValueError si el formato no es correcto.
        """
        vat_no_prefix = vat[2:] if vat.startswith('ES') else vat
        if re.match(r'^\d{8}[A-Z]$', vat_no_prefix):
            return 'person'
        if re.match(r'^[A-Z]\d{8}$', vat_no_prefix):
            return 'company'
        raise ValueError('El número de NIF no es válido. Formatos aceptados: 00000000A o A00000000.')


    def create_partner_in_db(self, name, email, company_name, vat, street, street2, zip, city, state_id, phone, cloud_url, company_type):
        """
        Crea un res.partner en la base de datos actual con los datos proporcionados.
        """
        env = request.env
        partner_vals = {
            'name': name,
            'email': email,
            'company_name': company_name,
            'vat': vat,
            'street': street,
            'street2': street2,
            'zip': zip,
            'city': city,
            'state_id': state_id,
            'phone': phone,
            'cloud_url': cloud_url,
            'company_type': company_type,
        }
        partner = env['res.partner'].with_context(no_vat_validation=True, lang='es_ES').sudo().create(partner_vals)
        portal_wizard = request.env['portal.wizard'].sudo().with_context(active_ids=[partner.id]).create({})
        portal_user = portal_wizard.user_ids
        portal_user.email = partner.email
        portal_user.sudo().action_grant_access()

        return partner

    def _get_odoo_server_ip(self):
        """Devuelve la IP del servidor Odoo.

        Primero intenta obtenerla consultando la interfaz de red y, si no es
        posible, la lee de un archivo de configuración estándar.
        """
        ip_addr = None

        # Intento automático leyendo la IP asociada a la interfaz de salida
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip_addr = s.getsockname()[0]
        except Exception as exc:
            _logger.warning("WS No se pudo obtener la IP automáticamente: %s", exc)

        # Si no se obtuvo o es localhost, leer la IP de un archivo de
        # configuración. La ruta puede especificarse en las variables de
        # entorno ODOO_CONF u ODOO_RC, de lo contrario se usa la ruta por
        # defecto '/etc/odoo18.conf'.
        if not ip_addr or ip_addr.startswith("127."):
            conf_path = (
                os.environ.get("ODOO_CONF")
                or os.environ.get("ODOO_RC")
                or "/etc/odoo18.conf"
            )
            if os.path.exists(conf_path):
                conf = configparser.ConfigParser()
                conf.read(conf_path)
                for option in ["httpconf"]:
                    if conf.has_option("options", option):
                        ip_addr = conf.get("options", option)
                        if ip_addr:
                            break

        return ip_addr or "127.0.0.1"

    def create_subdomain_in_ovh(self, subdomain):
        """Crea el subdominio en OVH usando la API."""

        config_file = '/etc/letsencrypt/ovhodoo.ini'  # Asegúrate de que esta ruta es correcta

        _logger.info("Intentando leer el archivo de configuración: %s", config_file)
        if not os.path.isfile(config_file):
            message = f"No se pudo leer el archivo de configuración: {config_file}"
            _logger.error(message)
            raise Exception("Archivo de configuración de OVH no encontrado o inaccesible.")

        parser = configparser.ConfigParser()
        try:
            read_files = parser.read(config_file)
            if not read_files:
                raise OSError(f"No se pudo abrir el archivo {config_file}")
            if 'ovh' not in parser:
                raise KeyError('ovh')

            config = parser['ovh']
            endpoint = config['dns_ovh_endpoint']
            application_key = config['dns_ovh_application_key']
            application_secret = config['dns_ovh_application_secret']
            consumer_key = config['dns_ovh_consumer_key']
            _logger.info("Configuración de OVH leída correctamente.")
        except (OSError, KeyError, configparser.Error) as exc:
            _logger.exception(
                "Error al procesar la configuración de OVH en el archivo %s", config_file
            )
            raise Exception(f"Error en la configuración de OVH: {exc}") from exc

        client = ovh.Client(
            endpoint=endpoint,
            application_key=application_key,
            application_secret=application_secret,
            consumer_key=consumer_key,
        )

        domain = "factuoo.com"
        ip_servidor_odoo = self._get_odoo_server_ip()

        try:
            _logger.info(
                "Creando registro A para el subdominio '%s.%s' apuntando a %s",
                subdomain,
                domain,
                ip_servidor_odoo,
            )
            response = client.post(
                f"/domain/zone/{domain}/record",
                fieldType="A",
                subDomain=subdomain,
                target=ip_servidor_odoo,
                ttl=3600,
            )
            client.post(f"/domain/zone/{domain}/refresh")
            _logger.info(
                "Subdominio '%s.%s' creado exitosamente en OVH apuntando a %s.",
                subdomain,
                domain,
                ip_servidor_odoo,
            )
        except ovh.exceptions.APIError:
            _logger.exception(
                "Error al crear el subdominio '%s.%s' en OVH", subdomain, domain
            )
            raise

    def install_modules_in_db(self, db_name, modules_list):
        """
        Instala los módulos seleccionados en la base de datos clonada.
        """
        if not modules_list:
            return  # No hay módulos para instalar

        # Cambiar el contexto a la nueva base de datos
        registry = Registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            # Instalar los módulos
            module_obj = env['ir.module.module']
            modules_to_install = module_obj.search([('name', 'in', modules_list)])
            if modules_to_install:
                modules_to_install.button_immediate_install()

    def create_user_in_db(self, db_name, email, name, subdomain, company_name,
                          street, street2, zip_code, city, state_id, phone):
        registry = Registry(db_name)
        #REQUISITOS
        # La base de datos a clonar debe incluir la configuración de correo (por ejemplo, factuoo)
        # El mail de la compañía se usará como remitente para el envío automático de la invitación, debe ser del mismo dominio que la base de datos (registro@factuoo.com)
        # Ambas configuraciones se limpian al final con el método clean
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Actualizar la única compañía existente y su partner relacionado
            company = env['res.company'].search([], limit=1)
            if company:
                company.sudo().write({'name': company_name})
                partner_vals = {
                    'name': company_name,
                    'email': email,
                    'street': street,
                    'street2': street2,
                    'zip': zip_code,
                    'city': city,
                    'phone': phone,
                }
                if state_id:
                    partner_vals['state_id'] = state_id
                company.sudo().partner_id.write(partner_vals)
                _logger.info(f"Nombre y datos de la compañía actualizados a: {company_name}")
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
        
        registry = Registry(db_name)
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

            
    def clean_mail_server(self, db_name):
        """
        Elimina la configuración de servidor de correo y limpia el email de la compañía.
        """
        registry = Registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Limpiar el servidor de correo saliente
            mail_server = env['ir.mail_server'].search([], limit=1)
            if mail_server:
                mail_server.sudo().unlink()
                _logger.info(f"Servidor de correo eliminado en la base de datos '{db_name}'")
          

            cr.commit()       
            
    @http.route('/get_zip_list', type='http', auth='public', methods=['GET'], website=True)
    def get_res_city_zip(self, **kwargs):
        searchTerm = kwargs.get('searchTerm', '') 
        page = int(kwargs.get('page', 1))
        pageSize = int(kwargs.get('pageSize', 20))

        try:
            page = int(page)
            pageSize = int(pageSize)
        except ValueError:
            page, pageSize = 1, 20

        city_ids = request.env['res.city'].sudo().search(
            [('name', '=ilike', "%" + searchTerm + "%")],
            limit=pageSize,
            offset=(page - 1) * pageSize
        ).ids

        zip_ids = request.env['res.city.zip'].sudo().search_read(
            domain=['|', 
                    ('name', '=ilike', "%" + searchTerm + "%"),
                    ('city_id', 'in', city_ids)],
            fields=['name', 'city_id'],
            limit=pageSize,
            offset=(page - 1) * pageSize
        )

        zip_ids = [{'id': record['id'], 'name': f"{record['name']} {record['city_id'][1]}"} for record in zip_ids]

        return request.make_response(
            json.dumps(zip_ids),
            headers=[("Content-Type", "application/json")]
        )
