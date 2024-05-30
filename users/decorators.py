from functools import wraps

from django.shortcuts import redirect


def anonymous_required(redirect_url):
    """
    Decorator for views that allow only unauthenticated users to access view.
    Usage:
    @anonymous_required(redirect_url='login/')
    def homepage(request):
        return render(request, 'homepage.html')

    :param redirect_url: URL to redirect to if user is authenticated
    Adapted from https://gist.github.com/m4rc1e/b28cfc9d24c3c2c47f21f2b89cffda86
    """
    def _wrapped(view_func, *args, **kwargs):
        def check_anonymous(request, *args, **kwargs):
            view = view_func(request, *args, **kwargs)
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view

        return check_anonymous

    return _wrapped


def ban_forbidden(redirect_url="/banned/"):
    """
    Decorator for views that do not allow banned users to access view.
    Usage:
    @ban_forbidden(redirect_url='login/')
    def homepage(request):
        return render(request, 'homepage.html')

    :param redirect_url: URL to redirect to if user is banned
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrap(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.is_banned:
                    return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return wrap
    return decorator


