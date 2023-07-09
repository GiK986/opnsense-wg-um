import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import OpnSenseApiClientForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from apps.utils.api_client import ApiClient


@login_required
# Create your views here.
def index(request):
    context = {
        "api_clients": request.user.opnsenseapiclient_set.all(),
        "segment": "index_api_clients",
    }
    return render(request, "opnsense_api_clients/index.html", context)


@login_required
def create(request):
    form = OpnSenseApiClientForm(request.user)
    context = {"form": form}
    if request.method == "POST":
        form = OpnSenseApiClientForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("index_api_clients")

    return render(request, "opnsense_api_clients/create.html", context)


@login_required
def update(request, pk):
    api_client = request.user.opnsenseapiclient_set.get(id=pk)
    form = OpnSenseApiClientForm(request.user, instance=api_client)
    context = {"form": form}
    if request.method == "POST":
        form = OpnSenseApiClientForm(request.user, request.POST, instance=api_client)
        if form.is_valid():
            form.save()
            return redirect("index_api_clients")

    return render(request, "opnsense_api_clients/update.html", context)


@login_required
def delete(request, pk):
    api_client = request.user.opnsenseapiclient_set.get(id=pk)
    if request.method == "POST":
        api_client.delete()
        return redirect("index_api_clients")

    context = {"api_client": api_client}
    return render(request, "opnsense_api_clients/delete.html", context)


@login_required
def set_default(request, pk):
    current_api_client = request.user.default_api_client
    set_default_api_client = request.user.opnsenseapiclient_set.get(id=pk)

    if current_api_client and current_api_client != set_default_api_client:
        current_api_client.is_default = False
        current_api_client.save()

        set_default_api_client.is_default = True
        set_default_api_client.save()

    return redirect(request.META['HTTP_REFERER'])


@login_required
@require_POST
@csrf_exempt
def test_connection(request):
    if request.method == "POST":
        data = json.loads(request.body)
        base_url = data.get('base_url')
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        api_client = ApiClient(base_url=base_url, api_key=api_key, api_secret=api_secret)
        result = api_client.test_connection()
        if result[0]:
            return JsonResponse({'status': 'success', 'message': result[1]})

        return JsonResponse({'status': 'error', 'message': result[1]})
