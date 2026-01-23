# This handles saving the specific employee data (salary, employee ID, etc.) to the database.
from app.extensions import db
from app.models.employee import Employee

class EmployeeRepository:
    """Repository for Employee model operations."""
    
    @staticmethod
    def create(user_id, **kwargs):
        """Create a new employee profile (Manager or Cashier) and commit immediately."""
        employee = Employee(user_id=user_id, **kwargs)
        db.session.add(employee)
        db.session.commit()
        return employee
    
    @staticmethod
    def create_without_commit(user_id, **kwargs):
        """
        Create a new employee profile WITHOUT committing (for transactional operations).
        Use this when creating Employee + User atomically.
        
        Must be followed by db.session.commit() or will be rolled back.
        """
        employee = Employee(user_id=user_id, **kwargs)
        db.session.add(employee)
        db.session.flush()  # Generate ID but don't commit yet
        return employee

    @staticmethod
    def get_by_user_id(user_id):
        """Get employee by user ID."""
        return Employee.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def update(employee, **kwargs):
        """Update employee attributes."""
        for key, value in kwargs.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
        db.session.commit()
        return employee
    
    @staticmethod
    def delete(employee):
        """Delete an employee."""
        db.session.delete(employee)
        db.session.commit()
    
    @staticmethod
    def get_all(page=1, per_page=20):
        """Get all employees with pagination."""
        return Employee.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )