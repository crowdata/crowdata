# from: https://djangosnippets.org/snippets/2179/
from django.conf import settings
USER_ATTR_NAME = getattr(settings, 'LOCAL_USER_ATTR_NAME', '_current_user')

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
_thread_locals = local()

from new import instancemethod
def _do_set_current_user(user_fun):
    setattr(_thread_locals, USER_ATTR_NAME, instancemethod(user_fun, _thread_locals, type(_thread_locals)))

def _set_current_user(user=None):
    '''
    Sets current user in local thread.

    Can be used as a hook e.g. for shell jobs (when request object is not
    available).
    '''
    _do_set_current_user(lambda self: user)

class LocalUserMiddleware(object):
    def process_request(self, request):
        # request.user closure; asserts laziness; memoization is implemented in
        # request.user (non-data descriptor)
        _do_set_current_user(lambda self: getattr(request, 'user', None))

def get_current_user():
    current_user = getattr(_thread_locals, USER_ATTR_NAME, None)
    return current_user() if current_user else current_user
