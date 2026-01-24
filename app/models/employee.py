from datetime import datetime
from app.extensions import db

class Employee(db.Model):
    """Employee profile extending User model."""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Personal Information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    
    # Address Information (for payroll, emergency contact)
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Employment Information
    employee_id = db.Column(db.String(20), unique=True)
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    salary = db.Column(db.Float)
    shift_start = db.Column(db.Time)
    shift_end = db.Column(db.Time)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def is_manager(self):
        """Check if employee is a manager."""
        return self.user.role == 'manager'

    @property
    def is_cashier(self):
        """Check if employee is a cashier."""
        return self.user.role == 'cashier'
    
    @property
    def full_name(self):
        """Get employee's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "Unknown"
    
    @property
    def full_address(self):
        """Get formatted full address."""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        
        city_state_zip = []
        if self.city:
            city_state_zip.append(self.city)
        if self.state:
            city_state_zip.append(self.state)
        if self.postal_code:
            city_state_zip.append(self.postal_code)
        
        if city_state_zip:
            parts.append(', '.join(city_state_zip))
        
        if self.country:
            parts.append(self.country)
        
        return '\n'.join(parts) if parts else None
    
    def to_dict(self, include_salary=False):
        """Convert employee to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'postal_code': self.postal_code,
                'country': self.country
            },
            'employee_id': self.employee_id,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'shift_start': self.shift_start.isoformat() if self.shift_start else None,
            'shift_end': self.shift_end.isoformat() if self.shift_end else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        # Only include salary if explicitly requested (privacy)
        if include_salary:
            data['salary'] = self.salary
        
        return data
    
    def __repr__(self):
        return f'<Employee {self.full_name} ({self.employee_id})>'