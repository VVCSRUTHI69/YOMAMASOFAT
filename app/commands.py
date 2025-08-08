import click
from flask.cli import with_appcontext
from .models import User, db

@click.command('create-user')
@click.argument('name')
@click.argument('email')
@click.argument('password')
@click.argument('role')
@with_appcontext
def create_user_command(name, email, password, role):
    """Creates a new user."""
    if User.query.filter_by(email=email).first():
        click.echo('Error: Email already exists.')
        return

    user = User(name=name, email=email, role=role)
    user.password = password
    db.session.add(user)
    db.session.commit()
    click.echo(f'User {name} created successfully with role {role}.')

from datetime import datetime, timedelta
import click
from .models import Request, AuditLog

# Define the escalation hierarchy
HIERARCHY = ['Faculty', 'HoD', 'DeptComm', 'InstituteComm', 'CentralComm']

@click.command('escalate-requests')
@with_appcontext
def escalate_requests_command():
    """Checks for and escalates overdue requests."""
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # Find requests that are not closed and haven't been updated in 7 days
    overdue_requests = Request.query.filter(
        Request.status.notin_(['Approved', 'Rejected', 'Closed']),
        Request.updated_at < seven_days_ago
    ).all()

    if not overdue_requests:
        click.echo('No overdue requests to escalate.')
        return

    click.echo(f'Found {len(overdue_requests)} overdue requests. Escalating...')

    for req in overdue_requests:
        current_role = req.current_handler_role
        try:
            current_index = HIERARCHY.index(current_role)
            if current_index + 1 < len(HIERARCHY):
                next_role = HIERARCHY[current_index + 1]
                req.current_handler_role = next_role
                req.status = f'Auto-escalated to {next_role}'

                # Log the system action
                audit_log = AuditLog(
                    request_id=req.id,
                    action_by=None, # System action
                    role='System',
                    action='Auto-Escalate',
                    notes=f'Request automatically escalated from {current_role} to {next_role} due to inactivity.'
                )
                db.session.add(audit_log)
                click.echo(f'Request #{req.id} escalated to {next_role}.')
            else:
                # Already at the top of the hierarchy, do nothing or log it
                click.echo(f'Request #{req.id} is at the highest escalation level and cannot be escalated further.')

        except ValueError:
            click.echo(f'Warning: Role {current_role} for request #{req.id} not found in HIERARCHY. Skipping.')

    db.session.commit()
    click.echo('Escalation process complete.')

def init_app(app):
    app.cli.add_command(create_user_command)
    app.cli.add_command(escalate_requests_command)
