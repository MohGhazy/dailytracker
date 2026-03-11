from django import forms
from .models import Kegiatan, Kategori
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class FormUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full border border-[#E5E7EB] rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#C6A969]/30 outline-none'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-[#E5E7EB] rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#C6A969]/30 outline-none'
            })
        }
        
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full border border-[#E5E7EB] rounded-lg px-3 py-2 pr-16 focus:ring-2 focus:ring-[#C6A969]/30 outline-none"
        })
    )

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full border border-[#E5E7EB] rounded-lg px-3 py-2 pr-16 focus:ring-2 focus:ring-[#C6A969]/30 outline-none"
        })
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full border border-[#E5E7EB] rounded-lg px-3 py-2 pr-16 focus:ring-2 focus:ring-[#C6A969]/30 outline-none"
        })
    )

class FormKegiatan(forms.ModelForm):
 class Meta:
  model = Kegiatan
  fields = ['judul', 'tanggal', 'waktu', 'kategori']
  widgets = {
   'judul': forms.TextInput(attrs={
        'class': 'w-full border border-[#E5E7EB] rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#C6A969]/30 outline-none',
        'placeholder': 'Masukkan judul kegiatan'
    }),
    'tanggal': forms.DateInput(attrs={
        'type': 'date',
        'class': 'w-full border border-[#E5E7EB] rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#C6A969]/30 outline-none'
    }),
    'waktu': forms.TimeInput(attrs={
        'type': 'time',
        'class': 'w-full border border-[#E5E7EB] rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#C6A969]/30 outline-none'
    }),
    'kategori': forms.Select(attrs={
        'class': 'w-full border border-[#E5E7EB] rounded-lg px-3 py-2 focus:ring-2 focus:ring-[#C6A969]/30 outline-none'
    }),
  }

 def __init__(self, *args, **kwargs):
  user = kwargs.pop('user', None)
  super().__init__(*args, **kwargs)

  if user:
   self.fields['kategori'].queryset = Kategori.objects.filter(user=user)