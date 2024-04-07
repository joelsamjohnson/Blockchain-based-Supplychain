from django import template

register = template.Library()

USER_TYPES = {
    'S': 'Supplier',
    'M': 'Manufacturer',
    'D': 'Distributor',
    'R': 'Retailer',
    'C': 'Customer',
}

@register.filter(name='user_type_full')
def user_type_full(value):
    return USER_TYPES.get(value, 'Unknown')  # Default to 'Unknown' if not found
