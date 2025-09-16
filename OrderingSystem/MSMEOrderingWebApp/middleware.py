from django.urls import reverse
from django.shortcuts import redirect
from MSMEOrderingWebApp.models import BusinessDetails, BusinessOwnerAccount

class BusinessOwnerSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = [
            reverse('login'),
            reverse('logout'),
            reverse('force_change'),
            reverse('verify_email'),
            reverse('online_payment_details'),
            reverse('upload_logo'),
        ]
        allowed_prefixes = ['/static/', '/media/', '/admin']

        # ✅ Allow static, media, login, logout, and force_change
        if any(request.path.startswith(prefix) for prefix in allowed_prefixes) or request.path in allowed_paths:
            return self.get_response(request)

        owner_id = request.session.get('owner_id')
        if owner_id:
            try:
                owner = BusinessOwnerAccount.objects.get(id=owner_id)

                # ✅ If first_login2 is still True → restrict access
                if owner.first_login2:
                    # Allow access only to settings module
                    if not request.path.startswith(reverse('settings')):
                        return redirect('settings')

            except BusinessOwnerAccount.DoesNotExist:
                pass

        return self.get_response(request)