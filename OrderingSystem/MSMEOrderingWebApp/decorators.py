from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from functools import wraps

def login_required_session(view_func):
    @wraps(view_func)
    @never_cache
    def wrapper(request, *args, **kwargs):
        if not request.session.get('owner_id') and not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
