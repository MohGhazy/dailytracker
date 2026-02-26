from django.db import models
from django.contrib.auth.models import User

class Kegiatan(models.Model):
 pengguna = models.ForeignKey(User, on_delete=models.CASCADE)
 judul = models.CharField(max_length=200)
 tanggal = models.DateField()
 waktu = models.TimeField()
 kategori = models.ForeignKey('Kategori', on_delete=models.SET_NULL, null=True, blank=True)
 selesai = models.BooleanField(default=False)
 dibuat = models.DateTimeField(auto_now_add=True)
 class Meta:
  verbose_name_plural = "Kegiatan"
     
 def __str__(self):
  return self.judul
 
class Kategori(models.Model):
 user = models.ForeignKey(User, on_delete=models.CASCADE)
 nama = models.CharField(max_length=100)
 class Meta:
  verbose_name_plural = "Kategori"

 def __str__(self):
  return self.nama