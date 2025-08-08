from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .decorators import role_required
from .models import db, Request, AuditLog

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Admin':
        return render_template('admin_dashboard.html')
    elif current_user.role == 'Faculty':
        return render_template('faculty_dashboard.html')
    else: # Default to student
        requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.created_at.desc()).all()
        return render_template('student_dashboard.html', requests=requests)

@main.route('/admin-only')
@login_required
@role_required('Admin')
def admin_only():
    return "Welcome, Admin!"

@main.route('/request/new', methods=['GET', 'POST'])
@login_required
@role_required('Student')
def create_request():
    if request.method == 'POST':
        module = request.form.get('module')
        req_type = request.form.get('type')
        description = request.form.get('description')

        new_request = Request(
            user_id=current_user.id,
            module=module,
            type=req_type,
            description=description,
            status='Submitted',
            current_handler_role='Faculty Advisor' # As per escalation path
        )
        db.session.add(new_request)
        db.session.flush() # To get the new_request.id for the audit log

        audit_log = AuditLog(
            request_id=new_request.id,
            action_by=current_user.id,
            role=current_user.role,
            action='Submitted',
            notes='Request submitted by student.'
        )
        db.session.add(audit_log)
        db.session.commit()

        flash('Your request has been submitted successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('create_request.html')
