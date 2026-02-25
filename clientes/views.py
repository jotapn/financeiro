from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ClienteForm
from .models import Cliente


class ClienteListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes/list.html"
    context_object_name = "clientes"
    paginate_by = 25
    permission_required = "clientes.view_cliente"


class ClienteDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Cliente
    template_name = "clientes/detail.html"
    context_object_name = "cliente"
    permission_required = "clientes.view_cliente"


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes:list")
    permission_required = "clientes.add_cliente"


class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes:list")
    permission_required = "clientes.change_cliente"
