from datetime import datetime
from app.extensions import db

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    employee_id = db.Column(db.String(20), unique=True)
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    salary = db.Column(db.Float)
    shift_start = db.Column(db.Time)
    shift_end = db.Column(db.Time)

    @property
    def is_manager(self):
        return self.user.role == 'manager'

    @property
    def is_cashier(self):
        return self.user.role == 'cashier'