from django.db import models
from django.contrib.auth.models import User

class Kegiatan(models.Model):
    pengguna = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True
    )
    judul = models.CharField(max_length=200)
    tanggal = models.DateField(db_index=True)
    waktu = models.TimeField(db_index=True)
    kategori = models.ForeignKey(
        'Kategori',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    selesai = models.BooleanField(default=False, db_index=True)
    dibuat = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Kegiatan"
        indexes = [
            models.Index(fields=['pengguna', 'tanggal']),
            models.Index(fields=['pengguna', 'selesai']),
            models.Index(fields=['tanggal', 'waktu']),
        ]

    def __str__(self):
        return self.judul
 
class Kategori(models.Model):
 user = models.ForeignKey(User, on_delete=models.CASCADE)
 nama = models.CharField(max_length=100)
 class Meta:
  verbose_name_plural = "Kategori"

 def __str__(self):
  return self.nama