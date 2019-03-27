from django.contrib import admin
from .models.user import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

# Register your models here.
class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MyUserChangeForm, self).__init__(*args, **kwargs)


class MyUserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update({
        'duplicate_email': 'email username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MyUserCreationForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def save(self, commit=True):
        user = super(MyUserCreationForm, self).save(commit)
        user.save()
        signal_kwargs = {}
        signals.user_signed_up.send(sender=user.__class__,
                                    request=self.request,
                                    user=user,
                                    **signal_kwargs)
        return user


@admin.register(User)
class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = (
        'id', 'email', 'first_name', 'last_name', 'administration_groups',
        'is_superuser',
    )
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ('id',)

    def administration_groups(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])


    staff_filter = {'customer_profile__allow_staff': True,}


    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super(MyUserAdmin, self).get_form(request, obj, **kwargs)

        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return AdminFormWithRequest