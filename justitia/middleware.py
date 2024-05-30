import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import authenticate

logger = logging.getLogger('login_attempts')


class LoginAttemptLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == '/login/' and request.method == 'POST':
            username = request.POST.get('username')
            user = authenticate(request, username=username)
            if user is not None:
                logger.info(f"Successful login attempt: {username}")
            else:
                logger.warning(f"Failed login attempt: {username}")


class AdminPageLoadLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if '/admin' in request.path:
            logger.info(f'Admin page accessed by user: {request.user.username}')