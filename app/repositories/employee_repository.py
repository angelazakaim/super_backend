# This handles saving the specific employee data (salary, employee ID, etc.) to the database.
from app.extensions import db
from app.models.employee import Employee

class EmployeeRepository:
    """Repository for Employee model operations."""
    
    @staticmethod
    def create(user_id, **kwargs):
        """Create a new employee profile (Manager or Cashier)."""
        employee = Employee(user_id=user_id, **kwargs)
        db.session.add(employee)
        db.session.commit()
        return employee

    @staticmethod
    def get_by_user_id(user_id):
        return Employee.query.filter_by(user_id=user_id).first()