from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    # Paths exempt from canonical host redirect (e.g., health checks from orchestrators)
    EXEMPT_PATHS = ["/health/"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        canonical_host = getattr(settings, "CANONICAL_HOST", "")
        if canonical_host and not settings.DEBUG:
            # Skip redirect for exempt paths (health checks, etc.)
            if request.path in self.EXEMPT_PATHS:
                return self.get_response(request)
            request_host = request.get_host().split(":")[0].lower()
            if request_host != canonical_host.lower():
                scheme = "https" if request.is_secure() else request.scheme
                redirect_url = f"{scheme}://{canonical_host}{request.get_full_path()}"
                return HttpResponsePermanentRedirect(redirect_url)
        return self.get_response(request)
