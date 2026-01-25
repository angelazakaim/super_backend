"""Enumerations for the application."""
from enum import Enum


class UserRole(str, Enum):
    """
    User role enumeration.
    
    Inherits from str so values can be used directly as strings
    (e.g., in database queries, JSON serialization).
    
    Usage:
        user.role = UserRole.CUSTOMER
        if user.role == UserRole.ADMIN:
            ...
    """
    ADMIN = 'admin'
    CUSTOMER = 'customer'
    MANAGER = 'manager'
    CASHIER = 'cashier'
    
    @classmethod
    def values(cls):
        """Get list of all role values."""
        return [role.value for role in cls]
    
    @classmethod
    def is_valid(cls, value):
        """Check if a value is a valid role."""
        return value in cls.values()
    
    @classmethod
    def staff_roles(cls):
        """Get all staff roles (cashier, manager, admin)."""
        return [cls.ADMIN.value, cls.MANAGER.value, cls.CASHIER.value]
    
    @classmethod
    def management_roles(cls):
        """Get management roles (manager, admin)."""
        return [cls.ADMIN.value, cls.MANAGER.value]


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    
    @classmethod
    def values(cls):
        """Get list of all status values."""
        return [status.value for status in cls]
    
    @classmethod
    def is_valid(cls, value):
        """Check if a value is a valid order status."""
        return value in cls.values()
    
    @classmethod
    def active_statuses(cls):
        """Get statuses for active orders (not cancelled/refunded)."""
        return [
            cls.PENDING.value,
            cls.CONFIRMED.value,
            cls.PROCESSING.value,
            cls.SHIPPED.value,
            cls.DELIVERED.value
        ]


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    
    @classmethod
    def values(cls):
        """Get list of all payment status values."""
        return [status.value for status in cls]
    
    @classmethod
    def is_valid(cls, value):
        """Check if a value is a valid payment status."""
        return value in cls.values()


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    PAYPAL = 'paypal'
    CASH = 'cash'
    BANK_TRANSFER = 'bank_transfer'
    
    @classmethod
    def values(cls):
        """Get list of all payment method values."""
        return [method.value for method in cls]
    
    @classmethod
    def is_valid(cls, value):
        """Check if a value is a valid payment method."""
        return value in cls.values()