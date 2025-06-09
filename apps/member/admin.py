from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Member, Group

# Register your models here.
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )


@admin.action(description="선택된 성원 복구")
def restore_members(modeladmin, request, queryset):
    queryset.update(deleted=False)


@admin.action(description="선택된 성원 활성화")
def active_members(modeladmin, request, queryset):
    queryset.update(dactiv=True)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("추가 정보", {"fields": ("name", "gender", "group", "active", "deleted")}),
    )
    list_display = ('id', 'username', 'name', 'gender', 'group', 'is_active', 'is_staff')
    list_filter = ('group', 'active', 'deleted', 'gender')
    search_fields = ('username', 'name', 'email' )

    actions = [active_members, restore_members]