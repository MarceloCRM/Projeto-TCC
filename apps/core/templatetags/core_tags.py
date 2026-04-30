from django import template

register = template.Library()

@register.filter(name='has_role')
def has_role(user, role_name):
    if user is None or not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=role_name).exists()

