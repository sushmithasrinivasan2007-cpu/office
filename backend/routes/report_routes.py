"""
Report Routes - Advanced Reporting & Exports
PDF invoices, CSV exports, custom reports
"""
from flask import Blueprint, request, jsonify
from utils.supabase_client import supabase

from services.email_automation_service import email_service
from datetime import datetime, timedelta
import json

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/invoice/create', methods=['POST'])
def create_invoice():
    """Create a new invoice from task data"""
    try:
        data = request.json
        company_id = data.get('company_id')
        client_id = data.get('client_id')
        task_ids = data.get('task_ids', [])
        items = data.get('items', [])

        if not company_id or not client_id:
            return jsonify({"error": "company_id and client_id are required"}), 400

        # Calculate totals
        subtotal = sum(item.get('quantity', 1) * item.get('rate', 0) for item in items)
        tax_percent = data.get('tax_percent', 18)
        tax_amount = subtotal * (tax_percent / 100)
        total = subtotal + tax_amount

        invoice_data = {
            'company_id': company_id,
            'client_id': client_id,
            'items': json.dumps(items),
            'subtotal': subtotal,
            'tax_percent': tax_percent,
            'tax_amount': tax_amount,
            'total_amount': total,
            'issue_date': data.get('issue_date', datetime.now().strftime('%Y-%m-%d')),
            'due_date': data.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')),
            'status': 'draft',
            'notes': data.get('notes', ''),
            'terms': data.get('terms', 'Payment due within 30 days'),
            'created_by': data.get('created_by')
        }

        res = supabase.table('invoices').insert(invoice_data).execute()

        if res.data:
            return jsonify({"message": "Invoice created", "invoice": res.data[0]}), 201

        return jsonify({"error": "Failed to create invoice"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/invoice/<invoice_id>/send', methods=['POST'])
def send_invoice(invoice_id):
    """Send invoice to client via email"""
    try:
        # Get invoice
        inv_res = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
        if not inv_res.data:
            return jsonify({"error": "Invoice not found"}), 404

        invoice = inv_res.data[0]

        # Get client email
        client_res = supabase.table('clients').select('email,name').eq('id', invoice['client_id']).execute()
        if not client_res.data:
            return jsonify({"error": "Client not found"}), 404

        client = client_res.data[0]

        # Generate PDF (placeholder)
        pdf_url = f"/invoices/{invoice_id}.pdf"
        # In production: use reportlab or weasyprint to generate PDF

        # Update invoice
        supabase.table('invoices').update({
            'status': 'sent',
            'payment_link_url': f"https://pay.yourapp.com/invoice/{invoice_id}"
        }).eq('id', invoice_id).execute()

        # Send email
        # email_service.send_invoice_email(client['email'], invoice, pdf_url)

        return jsonify({"message": "Invoice sent", "invoice_id": invoice_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/invoice/<invoice_id>/payment-link', methods=['POST'])
def generate_payment_link(invoice_id):
    """Generate payment link for invoice"""
    try:
        inv_res = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
        if not inv_res.data:
            return jsonify({"error": "Invoice not found"}), 404

        invoice = inv_res.data[0]

        # Create payment link
        # In production: integrate with a payment gateway (e.g., Stripe, PayPal)
        payment_link = {
            'url': f"https://pay.yourapp.com/invoice/{invoice_id}",
            'amount': float(invoice['total_amount'])
        }

        supabase.table('invoices').update({
            'payment_link_url': payment_link['url']
        }).eq('id', invoice_id).execute()

        return jsonify({"payment_link": payment_link}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/export/<company_id>/tasks', methods=['GET'])
def export_tasks_csv(company_id):
    """Export tasks as CSV"""
    try:
        tasks_res = supabase.table('tasks').select('*').eq('company_id', company_id).execute()
        tasks = tasks_res.data or []

        # Convert to CSV
        if not tasks:
            return jsonify({"csv": ""}), 200

        import csv
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=tasks[0].keys())
        writer.writeheader()
        writer.writerows(tasks)

        return jsonify({"csv": output.getvalue()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/employee-timesheet/<user_id>', methods=['GET'])
def generate_timesheet(user_id):
    """Generate weekly timesheet for employee"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({"error": "start_date and end_date required"}), 400

        # Get attendance records
        att_res = supabase.table('attendance').select('*').eq('user_id', user_id).gte('checkin_time', start_date).lte('checkin_time', end_date).execute()
        records = att_res.data or []

        # Group by date
        timesheet = {}
        for rec in records:
            d = rec['checkin_time'][:10]
            if d not in timesheet:
                timesheet[d] = {'entries': [], 'total_minutes': 0}
            timesheet[d]['entries'].append(rec)
            if rec.get('work_duration_minutes'):
                timesheet[d]['total_minutes'] += rec['work_duration_minutes']

        return jsonify({"timesheet": timesheet}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/financial-summary/<company_id>', methods=['GET'])
def financial_summary(company_id):
    """Monthly financial summary"""
    try:
        # Last 30 days payments
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

        pay_res = supabase.table('payments').select('amount,status,created_at').eq('company_id', company_id).gte('created_at', thirty_days_ago).execute()
        payments = pay_res.data or []

        total_disbursed = sum(p['amount'] for p in payments if p['status'] == 'completed')
        pending = sum(p['amount'] for p in payments if p['status'] == 'pending')

        # Expenses
        exp_res = supabase.table('expenses').select('amount,status').eq('company_id', company_id).gte('created_at', thirty_days_ago).execute()
        expenses = exp_res.data or []
        total_expenses = sum(e['amount'] for e in expenses if e['status'] in ['approved', 'reimbursed'])

        return jsonify({
            'period': 'Last 30 days',
            'revenue': float(total_disbursed),
            'pending_payouts': float(pending),
            'expenses': float(total_expenses),
            'net': float(total_disbursed - total_expenses)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500