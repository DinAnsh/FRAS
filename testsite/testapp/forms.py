from django import forms

class UserRegistrationForm(forms.Form):
    clg_name = forms.CharField(
        label = 'College Name',
        max_length = 32
    )

    dept = forms.ChoiceField(choices=(
            ("Computer Science & Engineering", "Computer Science & Engineering"),
            ("Electrical Engineering", "Electrical Engineering")
            ), label="Choose Department"
    )

    username = forms.CharField(
        label = 'Admin Name',
        max_length = 32,
        #widget = forms.
    )
    email = forms.EmailField(
        label= 'Admin Mail',
        max_length=32,
    )
    password = forms.CharField(
        label = 'Password',
        max_length = 32,
        widget = forms.PasswordInput()
    )