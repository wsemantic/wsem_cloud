# /var/misAddons/wsem_verifactu_cloud/models/res_partner_endpoint.py
from odoo import http
from odoo.http import request

class ResPartnerEndpoint(http.Controller):

    @http.route('/api/create_partner', auth='api_key', methods=['POST'], csrf=False)
    def create_partner(self, **post):
        
        api_key = post.get('api_key')
        if api_key != 'f27b3a499870852a4b21f77b8065a01cbf740f78':
            return {'error': 'Invalid API key'}

        
        name = post.get('name')
        email = post.get('email')
        

        
        partner = request.env['res.partner'].sudo().create({
            'name': name,
            'email': email,
            
        })

        return {'partner_id': partner.id}
