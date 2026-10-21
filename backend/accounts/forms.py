from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter Username'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Phone Number'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if username.lower() in ['admin@csms.com', 'admin']:
            raise forms.ValidationError("This username is reserved for the system administrator.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def validate_unique(self):
        # Allow multiple registrations: do not block if username already exists
        pass

    def save(self, commit=True):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        name = self.cleaned_data.get('name')
        email = self.cleaned_data.get('email')
        phone = self.cleaned_data.get('phone')

        user = User.objects.filter(username__iexact=username).first()
        if user:
            # 1 user can register multiple times: update details and password
            user.name = name
            user.email = email
            user.phone = phone
            user.role = 'customer'
            user.set_password(password)
            if commit:
                user.save()
            return user
        else:
            user = super().save(commit=False)
            user.username = username
            user.role = 'customer'
            user.set_password(password)
            if commit:
                user.save()
            return user


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Phone Number'}),
        }


class AdminCustomerEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'phone', 'role']
        widgets = {
            'name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Phone Number'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
