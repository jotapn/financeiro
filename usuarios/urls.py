from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("", views.AdminDashboardView.as_view(), name="dashboard"),
    path("usuarios/", views.UsuarioListView.as_view(), name="users_list"),
    path("usuarios/novo/", views.UsuarioCreateView.as_view(), name="users_create"),
    path("usuarios/<int:pk>/", views.UsuarioDetailView.as_view(), name="users_detail"),
    path("usuarios/<int:pk>/editar/", views.UsuarioUpdateView.as_view(), name="users_update"),
    path("usuarios/<int:pk>/senha/", views.UsuarioPasswordView.as_view(), name="users_password"),
    path("grupos/", views.GrupoListView.as_view(), name="groups_list"),
    path("grupos/novo/", views.GrupoCreateView.as_view(), name="groups_create"),
    path("grupos/<int:pk>/", views.GrupoDetailView.as_view(), name="groups_detail"),
    path("grupos/<int:pk>/editar/", views.GrupoUpdateView.as_view(), name="groups_update"),
]
