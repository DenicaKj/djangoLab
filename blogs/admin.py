from django.contrib import admin
from django import forms
from django.contrib.admin import DateFieldListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.forms import ClearableFileInput
from django.http import HttpResponseForbidden
from django.db import models

from .models import Blog, Comment, CustomUser, BlogFile


# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", "date",)
    exclude = ("user",)

    def save_model(self, request, obj, form, change):
        field_value = form.cleaned_data.get('blog')
        if obj and request.user in field_value.user.blocked_users.all():
            obj.user = request.user
            return PermissionDenied("You don't have permission to comment on this blog.")
        else:
            obj.user = request.user
            super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'blog':
            blogs=Blog.objects.all()
            for blog in blogs:
                if request.user in blog.user.blocked_users.all():
                    kwargs['queryset'] = Blog.objects.exclude(id=blog.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        if obj and (request.user == obj.user or request.user.is_superuser):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if obj and (request.user == obj.user or request.user == obj.blog.user or request.user.is_superuser):
            return True
        return False

    def has_add_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True

admin.site.register(Comment, CommentAdmin)


class BlogFileInline(admin.TabularInline):
    model = BlogFile
    extra = 1
    readonly_fields = ('file',)
    def has_add_permission(self, request, obj=None):
        return True

class BlogAdmin(admin.ModelAdmin):
    inlines = [BlogFileInline,]
    list_display = ("title", "user",)
    list_filter = (("date",DateFieldListFilter),)
    search_fields = ("title", "content",)
    exclude = ("user",)

    def has_delete_permission(self, request, obj=None):
        if obj and (request.user == obj.user or request.user.is_superuser):
            return True
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj=Blog.objects.filter(id=object_id).first()
        if obj and request.user in obj.user.blocked_users.all():
            return HttpResponseForbidden("You don't have permission to view this blog.")
        return super().change_view(request, object_id, form_url, extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        for blog in qs:
            if request.user in blog.user.blocked_users.all():
                qs = qs.exclude(id=blog.id)

        return qs

    def has_change_permission(self, request, obj=None):
        if obj and (request.user == obj.user or request.user.is_superuser):
            return True
        return False

    def has_add_permission(self, request):
        return True

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Blog, BlogAdmin)


class CustomUserAdmin(UserAdmin):
    add_permission = 'auth.add_user'
    fieldsets = UserAdmin.fieldsets + (
        ('Blocked Users', {'fields': ('blocked_users',)}),
    )
    filter_horizontal = ('blocked_users',)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user==obj:
            return True
        return False
    def has_add_permission(self, request):
        return True

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'blocked_users':
            # Filter the queryset for the foreign key field
            kwargs['queryset'] = CustomUser.objects.exclude(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



admin.site.register(CustomUser, CustomUserAdmin)
