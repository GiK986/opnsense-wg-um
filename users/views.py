from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return render(request, "users/sing_up.html")
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, "Email already exists")
                    return render(request, "users/sing_up.html")
                else:
                    user = User.objects.create_user(
                        username=username, email=email, password=password, first_name=first_name, last_name=last_name
                    )
                    user.save()
                    messages.success(request, "User created")
                    return redirect("login")
        else:
            messages.error(request, "Passwords do not match")
            return render(request, "users/sing_up.html")

    return render(request, "users/sing_up.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials")
            return render(request, "users/login.html")
    return render(request, "users/login.html")


def logout_user(request):
    logout(request)
    messages.success(request, "You are now logged out")
    return redirect("login")
