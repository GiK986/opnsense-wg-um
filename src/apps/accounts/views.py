from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic as views
from django.urls import reverse_lazy

from .forms import LoginForm, RegistrationForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm, \
    UserProfileForm
from django.contrib.auth import views as auth_views


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


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You are now logged out")
    return redirect("login")


class SampleView(views.TemplateView):
    template_name = "home/sample-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "api_client": self.request.user.default_api_client,
            "page": {
                "title": "Sample Page",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                ]
            }

        })
        return context


class UserRegistrationView(views.CreateView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your account has been created")
        return response


class UserLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "You are now logged in")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)

        return response


class UserLogoutView(views.RedirectView):
    url = reverse_lazy("login")

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You are now logged out")
        return super().get(request, *args, **kwargs)


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = UserPasswordResetForm

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Password reset email has been sent")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)

        return response


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = UserPasswordChangeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page": {
                "title": "Change Password",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "Profile", "url": reverse_lazy("profile")},
                ]
            }

        })
        return context


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page": {
                "title": "Changed Password",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"name": "Profile", "url": reverse_lazy("profile")},
                ]
            }

        })
        return context


class UserProfileView(views.UpdateView):
    template_name = 'accounts/profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page": {
                "title": "Profile",
                "breadcrumbs": [
                    {"name": "Dashboard", "url": reverse_lazy("dashboard")},
                ]
            }

        })
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your account has been updated")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, error)

        return response
