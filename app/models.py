from datetime import datetime
from app import db, login_manager, bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(50), nullable=False, default='Student') # e.g., Student, Faculty, FA, HoD, Admin

    requests = db.relationship('Request', backref='author', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='actor', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.role}')"

class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module = db.Column(db.String(100), nullable=False) # Exam, Appeals, Help Desk
    type = db.Column(db.String(100), nullable=False) # Photocopy, Revaluation, etc.
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Submitted')
    current_handler_role = db.Column(db.String(50), nullable=False, default='Faculty Advisor')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    audit_logs = db.relationship('AuditLog', backref='request', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Request('{self.module}', '{self.type}', '{self.status}')"

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), nullable=False)
    action_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable for system actions
    role = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(100), nullable=False) # e.g., 'Submitted', 'Approved', 'Escalated'
    notes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"AuditLog('{self.action}', '{self.timestamp}')"

class AnonymousSubmission(db.Model):
    __tablename__ = 'anonymous_submissions'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    module = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"AnonymousSubmission('{self.module}', '{self.created_at}')"
