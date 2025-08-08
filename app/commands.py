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

def init_app(app):
    app.cli.add_command(create_user_command)
