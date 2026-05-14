"""
Invoice Routes - Billing & PDF Generation
"""
from flask import Blueprint, request, jsonify
from utils.supabase_client import supabase
from services.email_automation_service import email_service
from datetime import datetime, timedelta
import json

invoice_bp = Blueprint('invoice_bp', __name__)

@invoice_bp.route('/', methods=['GET'])
def get_invoices():
    try:
        company_id = request.args.get('company_id')
        client_id = request.args.get('client_id')
        status = request.args.get('status')

        query = supabase.table('invoices').select('*').eq('company_id', company_id)

        if client_id:
            query = query.eq('client_id', client_id)
        if status:
            query = query.eq('status', status)

        res = query.order('issue_date', desc=True).execute()
        return jsonify({'invoices': res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@invoice_bp.route('/', methods=['POST'])
def create_invoice():
    try:
        data = request.json
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{data.get('company_id')[:8]}"

        # Calculate totals
        items = data.get('items', [])
        subtotal = sum(item['quantity'] * item['rate'] for item in items)
        tax_percent = data.get('tax_percent', 18)
        tax_amount = subtotal * (tax_percent / 100)
        total = subtotal + tax_amount

        invoice_data = {
            'invoice_number': invoice_number,
            'company_id': data.get('company_id'),
            'client_id': data.get('client_id'),
            'items': json.dumps(items),
            'subtotal': subtotal,
            'tax_percent': tax_percent,
            'tax_amount': tax_amount,
            'total_amount': total,
            'currency': data.get('currency', 'INR'),
            'issue_date': data.get('issue_date', datetime.now().strftime('%Y-%m-%d')),
            'due_date': data.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')),
            'status': 'draft',
            'notes': data.get('notes', ''),
            'terms': data.get('terms', 'Payment due within 30 days'),
            'created_by': data.get('created_by'),
            'created_at': datetime.now().isoformat()
        }

        res = supabase.table('invoices').insert(invoice_data).execute()
        return jsonify({'invoice': res.data[0]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@invoice_bp.route('/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    try:
        res = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
        if res.data:
            return jsonify({'invoice': res.data[0]}), 200
        return jsonify({"error": "Invoice not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@invoice_bp.route('/<invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    try:
        data = request.json
        allowed = ['items', 'subtotal', 'tax_percent', 'tax_amount', 'total_amount',
                   'issue_date', 'due_date', 'status', 'notes', 'terms']
        update_data = {k: v for k, v in data.items() if k in allowed}
        supabase.table('invoices').update(update_data).eq('id', invoice_id).execute()
        return jsonify({"message": "Invoice updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@invoice_bp.route('/<invoice_id>/send', methods=['POST'])
def send_invoice(invoice_id):
    try:
        res = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
        if not res.data:
            return jsonify({"error": "Invoice not found"}), 404

        invoice = res.data[0]

        # Get client email
        client_res = supabase.table('clients').select('email,name').eq('id', invoice['client_id']).execute()
        if not client_res.data:
            return jsonify({"error": "Client not found"}), 404

        client = client_res.data[0]

        # Send email
        html_body = f"""
        <h1>Invoice {invoice['invoice_number']}</h1>
        <p>Dear {client['name']},</p>
        <p>Please find your invoice attached. Total amount due: <strong>₹{invoice['total_amount']}</strong></p>
        <p>Due date: {invoice['due_date']}</p>
        <p><a href="{invoice.get('payment_link_url', '#')}">Pay Now</a></p>
        """

        email_service.send_email(client['email'], f"Invoice {invoice['invoice_number']}", html_body)

        # Update status
        supabase.table('invoices').update({'status': 'sent'}).eq('id', invoice_id).execute()

        return jsonify({"message": "Invoice sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@invoice_bp.route('/<invoice_id>/payment-link', methods=['POST'])
def generate_payment_link(invoice_id):
    """Generate Razorpay payment link"""
    try:
        res = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
        if not res.data:
            return jsonify({"error": "Invoice not found"}), 404

        invoice = res.data[0]

        # Payment link would be generated via Razorpay API
        payment_link = {
            'url': f"https://pay.smartsos.com/invoice/{invoice_id}",
            'amount': float(invoice['total_amount'])
        }

        supabase.table('invoices').update({
            'payment_link_url': payment_link['url']
        }).eq('id', invoice_id).execute()

        return jsonify({'payment_link': payment_link}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@invoice_bp.route('/<invoice_id>/pdf', methods=['GET'])
def generate_pdf(invoice_id):
    """Generate PDF invoice (placeholder)"""
    try:
        # Would use reportlab or weasyprint
        return jsonify({"message": "PDF generation not implemented", "url": f"/invoices/{invoice_id}.pdf"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500