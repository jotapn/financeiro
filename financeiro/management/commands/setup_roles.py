from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction


ROLE_DEFS = {
    "Admin": {
        "apps": ["auth", "clientes", "contratos", "financeiro"],
        "perms": ["add", "change", "delete", "view"],
    },
    "Operacional": {
        "apps": ["clientes", "contratos", "financeiro"],
        "perms": ["add", "change", "view"],
    },
    "Leitura": {
        "apps": ["clientes", "contratos", "financeiro"],
        "perms": ["view"],
    },
}


def _permission_codenames(app_label, model_names, actions):
    for model in model_names:
        for action in actions:
            yield f"{action}_{model}"


class Command(BaseCommand):
    help = "Cria grupos de perfis e aplica permissões padrão."

    @transaction.atomic
    def handle(self, *args, **options):
        model_map = {
            "auth": ["user", "group"],
            "clientes": ["cliente"],
            "contratos": ["servico", "contrato", "itemcontrato", "contratodocumento"],
            "financeiro": ["categoria", "centrocusto", "banco", "contabancaria", "lancamento"],
        }

        for role, config in ROLE_DEFS.items():
            group, _ = Group.objects.get_or_create(name=role)
            group.permissions.clear()

            for app_label in config["apps"]:
                model_names = model_map.get(app_label, [])
                codenames = list(
                    _permission_codenames(app_label, model_names, config["perms"])
                )
                perms = Permission.objects.filter(
                    content_type__app_label=app_label,
                    codename__in=codenames,
                )
                group.permissions.add(*perms)

            self.stdout.write(self.style.SUCCESS(f"Perfil '{role}' configurado."))
