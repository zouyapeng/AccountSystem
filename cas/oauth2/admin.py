from django.contrib import admin

from .models import Grant, AccessToken, RefreshToken, get_application_model


class RawIDAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)


class ApplicationAdmin(RawIDAdmin):
    readonly_fields = ("client_id", "user", "redirect_uris", "client_secret")
    exclude = ("client_type", "authorization_grant_type")
    list_filter = ("status", )
    list_display = ('name', 'user', 'status', 'created')
    list_filter = ('name', 'user', 'status')

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(ApplicationAdmin, self).get_readonly_fields(request, obj))
        if obj and obj.status == 2:
            print obj.status
            if "status" in fields:
                fields.remove("status")
        else:
            fields.append("status")
        return set(fields)

    def get_fields(self, request, obj=None):
        fields = super(ApplicationAdmin, self).get_fields(request, obj)
        if not obj or obj.status != 2:
            fields.remove("rejection_reason")
        return fields

Application = get_application_model()



admin.site.register(Application, ApplicationAdmin)
admin.site.register(Grant, RawIDAdmin)
admin.site.register(AccessToken, RawIDAdmin)
admin.site.register(RefreshToken, RawIDAdmin)
