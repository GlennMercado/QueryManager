from django.forms import ModelForm
from .models import Answer, Question, CustomUser, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from taggit.forms import TagField, TagWidget #changes

class AnswerForm(ModelForm):
    class Meta:
        model = Answer
        fields = ('solution',)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

class QuestionForm(ModelForm):
    tags = TagField()

    class Meta:
        model = Question
        fields = ('category', 'issue', 'detail', 'referenceform', 'tags')
        widgets = {
            'tags': TagWidget(), # changes
        }

class ProfileForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'region', 'email', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomUserCreationForm(UserCreationForm):
    region = forms.CharField(max_length=200, required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'region', 'first_name', 'last_name')

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        validate_password(password1, self.instance)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')

        if not password1:
            raise forms.ValidationError("Password is required.")

        return cleaned_data