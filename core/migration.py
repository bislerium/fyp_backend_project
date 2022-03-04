from django.db import migrations, models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.management import create_permissions


def add_group_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        create_permissions(app_config, apps=apps, verbosity=0)

    group, created = Group.objects.get_or_create(name='Administrador')
    # if created:
    #     permissions_qs = Permission.objects.filter(
    #         codename__in=['can_add_permision',
    #                       'can_change_permission',
    #                       'can_add_user',
    #                       'can_change_user',
    #                       'can_add_video',
    #                       'can_change_video',
    #                       'can_delete_video',
    #                       'can_add_documents',
    #                       'can_change_documents',
    #                       'can_delete_documents',
    #                       'can_add_news',
    #                       'can_change_news',
    #                       'can_delete_news',
    #                       'can_add_basics',
    #                       'can_change_basics',
    #                       'can_add_board',
    #                       'can_change_board',
    #                       'can_delete_board',
    #                       'can_add_history',
    #                       'can_change_history',
    #                       'can_delete_history',
    #                       'can_add_shortcuts',
    #                       'can_change_shortcuts',
    #                       'can_delete_shortcuts',]
    #     )
    #     group.permissions = permissions_qs
    group.save()
    # logger.info('Grupo Administrador Criado')


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.RunPython(add_group_permissions),
    ]
