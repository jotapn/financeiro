from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='clientes:list', permanent=False)),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', include('usuarios.urls')),
    path('clientes/', include('clientes.urls')),
    path('contratos/', TemplateView.as_view(template_name='contratos/placeholder.html'), name='contratos'),
    path('financeiro/', TemplateView.as_view(template_name='financeiro/placeholder.html'), name='financeiro'),
    path('djadmin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
