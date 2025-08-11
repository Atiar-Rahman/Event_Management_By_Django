from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name: str) -> bool:
    """
    Usage in templates:
      {% load role_tags %}
      {% if request.user|has_group:'organizer' %} ... {% endif %}

    Superusers always pass.
    """
    try:
        if not hasattr(user, 'is_authenticated') or not user.is_authenticated:
            return False
        if getattr(user, 'is_superuser', False):
            return True
        return user.groups.filter(name=group_name).exists()
    except Exception:
        return False
