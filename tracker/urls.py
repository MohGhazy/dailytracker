from django.urls import path
from . import views

urlpatterns = [
 path('dashboard/', views.dashboard, name='dashboard'),
 path('dashboard/total_kegiatan/', views.dashboard_total_kegiatan, name="dashboard_total_kegiatan"),
 path('kegiatan/', views.semua_kegiatan, name='semua_kegiatan'),
 path('tambah/', views.tambah_kegiatan, name='tambah_kegiatan'),
 path('edit/<int:id>/', views.edit_kegiatan, name='edit_kegiatan'),
 path('hapus/<int:id>/', views.hapus_kegiatan, name='hapus_kegiatan'),
 path('toggle/<int:id>/', views.toggle_selesai, name='toggle_selesai'),
 path('analytics/', views.analytics, name='analytics'),
 path('profile/', views.profile, name='profile'),
 path('kategori/tambah/', views.tambah_kategori, name='tambah_kategori'),
 path('kategori/edit/<int:id>/', views.edit_kategori, name='edit_kategori'),
 path('kategori/hapus/<int:id>/', views.hapus_kategori, name='hapus_kategori'),
]
