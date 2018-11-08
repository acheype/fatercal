from django import template

register = template.Library()


@register.filter('has_group')
def has_group(user, group_name):
    """
    Verify if the user is in the group
    :param user: the user connected
    :param group_name: the name of the group
    :return: a boolean
    """
    groups = user.groups.all().values_list('name', flat=True)
    if group_name in groups:
        return True
    else:
        return False