from datetime import date, timedelta
from tracker.models import Kegiatan
from django.shortcuts import get_object_or_404
from django.core.cache import cache

def get_filtered_kegiatan(user, filter_type="all", search_query=None):
 kegiatan = (
  Kegiatan.objects
  .filter(pengguna=user)
  .select_related('kategori')
 )
 
 if search_query:
  kegiatan = kegiatan.filter(judul__icontains=search_query)

 today = date.today()

 if filter_type == 'today':
  kegiatan = kegiatan.filter(tanggal=today)

 elif filter_type == 'week':
  start_week = today - timedelta(days=today.weekday())
  end_week = start_week + timedelta(days=6)
  kegiatan = kegiatan.filter(tanggal__range=(start_week, end_week))

 elif filter_type == 'done':
  kegiatan = kegiatan.filter(selesai=True)

 elif filter_type == 'pending':
  kegiatan = kegiatan.filter(selesai=False)

 return kegiatan.order_by('-tanggal', '-waktu')

def get_kegiatan(user, kegiatan_id):
 return get_object_or_404(
  Kegiatan,
  id=kegiatan_id,
  pengguna=user
 )

def toggle_kegiatan_status(user, kegiatan_id):
 kegiatan = get_object_or_404(
  Kegiatan,
  id=kegiatan_id,
  pengguna=user
 )

 kegiatan.selesai = not kegiatan.selesai
 kegiatan.save(update_fields=["selesai"])

 _invalidate_user_analytics_cache(user.id)

 return kegiatan

def create_kegiatan(user, form):
 kegiatan = form.save(commit=False)
 kegiatan.pengguna = user
 kegiatan.save()
 
 _invalidate_user_analytics_cache(user.id)

 return kegiatan

def update_kegiatan(kegiatan, form):
 updated = form.save()
 
 _invalidate_user_analytics_cache(kegiatan.pengguna.id)
 
 return updated

def delete_kegiatan(user, kegiatan_id):
 kegiatan = get_object_or_404(
  Kegiatan,
  id=kegiatan_id,
  pengguna=user
 )

 kegiatan.delete()
 
 _invalidate_user_analytics_cache(user.id)

def _invalidate_user_analytics_cache(user_id):
 keys = [
  f"analytics_{user_id}_week",
  f"analytics_{user_id}_month",
  f"analytics_{user_id}_all",
 ]

 for key in keys:
  cache.delete(key)