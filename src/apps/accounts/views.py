from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.views import generic as views
from django.urls import reverse_lazy

from .forms import LoginForm, RegistrationForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm, \
    UserProfileForm
from django.contrib.auth import views as auth_views


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
