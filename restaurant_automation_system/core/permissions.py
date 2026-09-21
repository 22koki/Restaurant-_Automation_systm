from rest_framework.permissions import BasePermission


def staff_role(user):
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return 'owner'
    profile = getattr(user, 'staff_profile', None)
    if not profile or not profile.active:
        return None
    return profile.role


class ActiveStaffPermission(BasePermission):
    def has_permission(self, request, view):
        return staff_role(request.user) is not None


class RolePermission(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        role = staff_role(request.user)
        return role in self.allowed_roles


class OwnerManagerPermission(RolePermission):
    allowed_roles = ('owner', 'manager')


class CashierManagerPermission(RolePermission):
    allowed_roles = ('owner', 'manager', 'cashier')


class ServicePermission(RolePermission):
    allowed_roles = ('owner', 'manager', 'waiter', 'cashier')


class KitchenPermission(RolePermission):
    allowed_roles = ('owner', 'manager', 'kitchen', 'waiter')


class InventoryPermission(RolePermission):
    allowed_roles = ('owner', 'manager', 'storekeeper')
