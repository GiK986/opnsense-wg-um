from django.shortcuts import render, redirect
from .forms import OpnSenseApiClientForm


# Create your views here.
def index(request):
    context = {
        "api_clients": request.user.opnsenseapiclient_set.all(),
    }
    return render(request, "opnsense_api_clients/index.html", context)


def create(request):
    form = OpnSenseApiClientForm(request.user)
    context = {"form": form}
    if request.method == "POST":
        form = OpnSenseApiClientForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("index_api_clients")

    return render(request, "opnsense_api_clients/create.html", context)


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


def delete(request, pk):
    api_client = request.user.opnsenseapiclient_set.get(id=pk)
    if request.method == "POST":
        api_client.delete()
        return redirect("index_api_clients")

    context = {"api_client": api_client}
    return render(request, "opnsense_api_clients/delete.html", context)
