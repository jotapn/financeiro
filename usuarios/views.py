from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, TemplateView, FormView

from .forms import GrupoForm, UsuarioCreateForm, UsuarioPasswordForm, UsuarioUpdateForm


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "usuarios/dashboard.html"


class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = "usuarios/users_list.html"
    context_object_name = "usuarios"
    paginate_by = 25
    permission_required = "auth.view_user"


class UsuarioDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = User
    template_name = "usuarios/users_detail.html"
    context_object_name = "usuario"
    permission_required = "auth.view_user"


class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = UsuarioCreateForm
    template_name = "usuarios/users_form.html"
    success_url = reverse_lazy("usuarios:users_list")
    permission_required = "auth.add_user"


class UsuarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioUpdateForm
    template_name = "usuarios/users_form.html"
    success_url = reverse_lazy("usuarios:users_list")
    permission_required = "auth.change_user"


class UsuarioPasswordView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = UsuarioPasswordForm
    template_name = "usuarios/users_password.html"
    permission_required = "auth.change_user"

    def dispatch(self, request, *args, **kwargs):
        self.usuario = get_object_or_404(User, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.usuario.set_password(form.cleaned_data["password1"])
        self.usuario.save()
        return redirect("usuarios:users_detail", pk=self.usuario.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = self.usuario
        return context


class GrupoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Group
    template_name = "usuarios/groups_list.html"
    context_object_name = "grupos"
    permission_required = "auth.view_group"


class GrupoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Group
    template_name = "usuarios/groups_detail.html"
    context_object_name = "grupo"
    permission_required = "auth.view_group"


class GrupoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Group
    form_class = GrupoForm
    template_name = "usuarios/groups_form.html"
    success_url = reverse_lazy("usuarios:groups_list")
    permission_required = "auth.add_group"


class GrupoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Group
    form_class = GrupoForm
    template_name = "usuarios/groups_form.html"
    success_url = reverse_lazy("usuarios:groups_list")
    permission_required = "auth.change_group"
