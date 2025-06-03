from typing import Any
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control mb-2",
                "placeholder": "Имя пользователя или email",
            })
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Пароль",
            }
        )


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control mb-2",
                "placeholder": "Email",
            }),
        required=True,
        help_text="Обзательное поле"
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control mb-2",
                "placeholder": "Имя пользователя",
            }
        )

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control mb-2",
                "placeholder": "Придумайте пароль",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Повторите пароль",
            }
        )

    def save(self, commit: bool = True) -> Any:
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
