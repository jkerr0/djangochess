from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_user_exists(value):
    try:
        User.objects.get(username=value)
    except User.DoesNotExist:
        raise ValidationError(
            'user does not exist',
            params={'value': value},
        )


class LobbyForm(forms.Form):
    white_player_name = forms.CharField(max_length=User._meta.get_field('username').max_length,
                                        validators=[validate_user_exists])
    black_player_name = forms.CharField(max_length=User._meta.get_field('username').max_length,
                                        validators=[validate_user_exists])
    game_id = forms.IntegerField(widget=forms.HiddenInput())
