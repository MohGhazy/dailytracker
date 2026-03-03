from datetime import date, datetime, timedelta
from django.db.models import Count, Q
from tracker.models import Kegiatan
from .utils import hitung_konsistensi

def parse_selected_date(date_param):
 today = date.today()
 try:
  return (
   datetime.strptime(date_param, "%Y-%m-%d").date()
   if date_param else today
  )
 except ValueError:
  return today

def get_daily_summary(user, selected_date):
 base_qs = (Kegiatan.objects.filter(
  pengguna=user,
  tanggal=selected_date
 ).select_related('kategori')
 )

 stats = base_qs.aggregate(
  total=Count('id'),
  selesai=Count('id', filter=Q(selesai=True))
 )

 total = stats["total"] or 0
 selesai = stats["selesai"] or 0
 belum = total - selesai
 konsistensi = hitung_konsistensi(total, selesai)

 return {
  "queryset": base_qs,
  "total": total,
  "selesai": selesai,
  "belum": belum,
  "konsistensi": konsistensi,
 }


def get_date_navigation(selected_date):
 return {
  "prev_date": selected_date - timedelta(days=1),
  "next_date": selected_date + timedelta(days=1),
  "today": date.today(),
 }