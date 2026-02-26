from django import forms
from .models import Kegiatan, Kategori
from django.contrib.auth.models import User


class FormUser(forms.ModelForm):
 class Meta:
  model = User
  fields = ['username', 'email']

class FormKegiatan(forms.ModelForm):
 class Meta:
  model = Kegiatan
  fields = ['judul', 'tanggal', 'waktu', 'kategori']
  widgets = {
   'judul': forms.TextInput(attrs={
        'class': 'border rounded px-3 py-2 w-full',
        'placeholder': 'Masukkan judul kegiatan'
    }),
    'tanggal': forms.DateInput(attrs={
        'type': 'date',
        'class': 'border rounded px-3 py-2 w-full'
    }),
    'waktu': forms.TimeInput(attrs={
        'type': 'time',
        'class': 'border rounded px-3 py-2 w-full'
    }),
    'kategori': forms.Select(attrs={
        'class': 'border rounded px-3 py-2 w-full'
    }),
  }

 def __init__(self, *args, **kwargs):
  user = kwargs.pop('user', None)
  super().__init__(*args, **kwargs)

  if user:
   self.fields['kategori'].queryset = Kategori.objects.filter(user=user)