from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        canonical_host = getattr(settings, "CANONICAL_HOST", "")
        if canonical_host and not settings.DEBUG:
            request_host = request.get_host().split(":")[0].lower()
            if request_host != canonical_host.lower():
                scheme = "https" if request.is_secure() else request.scheme
                redirect_url = f"{scheme}://{canonical_host}{request.get_full_path()}"
                return HttpResponsePermanentRedirect(redirect_url)
        return self.get_response(request)
