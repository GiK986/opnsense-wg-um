from django.shortcuts import redirect
from django.contrib import messages


def api_client_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Check if the user has a default_api_client property
        if hasattr(request.user, 'default_api_client')\
                and request.user.default_api_client is not None:
            # Call the view function if the user has the property
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to the create_api_client page if the user doesn't have the property
            message = "You need to create an API client first."
            messages.warning(request, message)
            return redirect('create_api_client')
    return wrapper
