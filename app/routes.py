from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from .decorators import role_required
from .models import db, User, Request, AuditLog, AnonymousSubmission

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
    elif current_user.role in ['Faculty', 'FA', 'HoD', 'DeptComm', 'InstituteComm', 'CentralComm']:
        # For simplicity, all faculty/committee roles share a similar dashboard view
        # The query below fetches requests assigned to the user's specific role
        requests = Request.query.filter_by(current_handler_role=current_user.role).order_by(Request.updated_at.asc()).all()
        return render_template('faculty_dashboard.html', requests=requests)
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

@main.route('/anonymous-submission', methods=['GET', 'POST'])
def anonymous_submission():
    if request.method == 'POST':
        module = request.form.get('module')
        description = request.form.get('description')

        submission = AnonymousSubmission(
            module=module,
            description=description
        )
        db.session.add(submission)
        db.session.commit()
        flash('Your anonymous submission has been received. Thank you for your feedback!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('anonymous_submission.html')

# Define the escalation hierarchy
HIERARCHY = ['Faculty', 'HoD', 'DeptComm', 'InstituteComm', 'CentralComm']

@main.route('/request/<int:request_id>')
@login_required
def request_details(request_id):
    req = Request.query.get_or_404(request_id)
    # Security check: only the author or the current handler can view
    if current_user.id != req.user_id and current_user.role != req.current_handler_role:
        abort(403)
    return render_template('request_details.html', request=req)

@main.route('/request/<int:request_id>/act', methods=['POST'])
@login_required
def process_request_action(request_id):
    req = Request.query.get_or_404(request_id)
    action = request.form.get('action')
    notes = request.form.get('notes')

    # Security check: only the current handler can take action
    if current_user.role != req.current_handler_role:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('main.dashboard'))

    if action == 'Approve':
        req.status = 'Approved'
        req.current_handler_role = 'Closed'
    elif action == 'Reject':
        req.status = 'Rejected'
        req.current_handler_role = 'Closed'
    elif action == 'Forward':
        try:
            current_index = HIERARCHY.index(current_user.role)
            if current_index + 1 < len(HIERARCHY):
                next_role = HIERARCHY[current_index + 1]
                req.current_handler_role = next_role
                req.status = f'Forwarded to {next_role}'
            else:
                # End of the line
                req.status = 'Escalated to Top Level'
                req.current_handler_role = 'Closed' # Or a special 'TopLevel' role
        except ValueError:
            flash('Could not determine next escalation step.', 'danger')
            return redirect(url_for('main.request_details', request_id=req.id))
    else:
        flash('Invalid action.', 'danger')
        return redirect(url_for('main.request_details', request_id=req.id))

    # Log the action
    audit_log = AuditLog(
        request_id=req.id,
        action_by=current_user.id,
        role=current_user.role,
        action=action,
        notes=notes
    )
    db.session.add(audit_log)
    db.session.commit()

    flash(f'Request has been {action}ed.', 'success')
    return redirect(url_for('main.dashboard'))

# ==== Admin Routes ====

@main.route('/admin/users')
@login_required
@role_required('Admin')
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@main.route('/admin/audit-trail')
@login_required
@role_required('Admin')
def view_audit_trail():
    page = request.args.get('page', 1, type=int)
    pagination = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=15
    )
    return render_template('audit_trail.html', pagination=pagination)
