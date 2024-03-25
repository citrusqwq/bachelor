from django import forms
from django.contrib.auth import hashers
from django.forms import ModelForm
from django.forms.widgets import EmailInput
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from api.models import MeetingVideo, UserCreationSecret
from users.models import CustomUser

class VideoForm(ModelForm):
    class Meta:
        model= MeetingVideo
        fields= ["videofile"]
        labels = {
            'videofile': _('Videodatei'),
        }

class UserCreationFormSecret(forms.Form):
    """A Form to check a UserCreationSecret.
    This form doesn't save any data.
    This form checks if the secret is valid and deletes it.
    """
    
    create_secret = forms.CharField(label=_("Einmalkennwort zum Erstellen eines Accounts"), 
        help_text=_("Das Einmalkennwort welches ihnen vom Adminstrator des Servers bereitgestellt wurde."),
        widget=forms.PasswordInput)

    def clean(self):
        """Custom clean method to check if create_secret is found in database

        Returns:
            Dict[str, Any] or None: If the secret is valid dict with key 'create_secret' or None if secret is invalid.
        """
        cleaned_data = super().clean()

        for secret in UserCreationSecret.objects.filter(valid_until__gt=now()):
            if hashers.check_password(cleaned_data["create_secret"], secret.password_hash):
                # one valid password was found
                # delete secret since a secret can only be used once
                secret.delete()
                return cleaned_data

        # not valid password was found in list of password_hashes
        self.add_error('create_secret', ValidationError(_("Einmalkennwort des Adminstrator falsch oder abgelaufen.")))

    def save(self, commit=True):
        """
        """
        return None
