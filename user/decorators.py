from django.contrib.auth.decorators import user_passes_test

def group_required(*group_names, login_url='sign-in'):
    def check(u):
        if not u.is_authenticated:
            return False
        if u.is_superuser:
            return True
        return u.groups.filter(name__in=group_names).exists()
    return user_passes_test(check, login_url=login_url)
