from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    JSONField,
    OneToOneField,
)
from drugstoc_inventory.model_utils import BaseModelMixin
from users.managers import UserManager

def default_user_metadata():
    return {"is_admin": False}

class User(AbstractUser):
    address = models.CharField(max_length=100, blank=True, null=True)
    metadata = JSONField(default=default_user_metadata)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Custom related name to avoid clashes
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',  # Custom related name to avoid clashes
        blank=True,
    )

    objects = UserManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.metadata.get('is_admin'):
            admin_group, created = Group.objects.get_or_create(name='Admin')
            self.groups.add(admin_group)
        else:
            admin_group = Group.objects.filter(name='Admin').first()
            if admin_group:
                self.groups.remove(admin_group)

    def __str__(self):
        return self.username


class BlacklistedAccessToken(BaseModelMixin):
    token = models.CharField(max_length=500, unique=True)
    blacklisted_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.token