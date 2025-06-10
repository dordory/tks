from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ActiveMemberManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class Member(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True)
    password = models.CharField(max_length=128, default='pbkdf2_sha256$260000$TEMP$yUQrzTYbf7yZi0G0CeIYks9OnL12ATSlRWWuvYz+Z8k=')

    GENDER_CHOICES = (
        ('d', '모름'),
        ('b', '형제'),
        ('s', '자매'),
    )

    name = models.CharField(max_length=20)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name='members',
        null=True
    )
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    objects = UserManager()
    active_only = ActiveMemberManager()

    def delete(self, *args, **kwargs):
        """ soft delete 처리 """
        self.deleted = True
        self.save()

    def __str__(self):
        return self.name