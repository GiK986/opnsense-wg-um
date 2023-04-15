from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# Create your views here.
def dashboard(request):
    context = {
        "user": request.user,
        "total_count": 100,
        "inactive_count": 25,
        "inactive_more_7days_count": 10,
        "clients": [
            {
                "interface": "wg0",
                "name": "John Doe",
                "uuid": "1234567890",
                "tunneladdress": "192.168.0.12",
                "lastHandshake": "2021-10-01 12:00:00",
                "config_url": "wg0.conf",
            }
        ],
    }
    return render(request, "dashboard/dashboard.html", context)
