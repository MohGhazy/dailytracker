from datetime import date, timedelta
from calendar import monthrange
from collections import OrderedDict
from django.db.models import Count, Q
from tracker.models import Kegiatan
from .utils import hitung_konsistensi, hitung_scale
from django.db.models.functions import ExtractWeekDay, ExtractDay, ExtractMonth, ExtractYear
from django.core.cache import cache

def get_period_range(user, range_type):
    today = date.today()
    semua = Kegiatan.objects.filter(pengguna=user)

    if range_type == "week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)

    elif range_type == "month":
        start = today.replace(day=1)
        last_day = monthrange(today.year, today.month)[1]
        end = today.replace(day=last_day)

    else:
        first = semua.order_by("tanggal").first()
        last = semua.order_by("-tanggal").first()
        start = first.tanggal if first else today
        end = last.tanggal if last else today

    return start, end


def build_analytics_data(user, range_type):    
    cache_key = f"analytics_{user.id}_{range_type}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        print("Mengambil data dari cache")
        return cached_data
    print("Mengambil data dari database")

    start_period, end_period = get_period_range(user, range_type)

    semua = (
        Kegiatan.objects
        .filter(
            pengguna=user,
            tanggal__range=[start_period, end_period]
        )
        .select_related("kategori")
    )
    selesai_qs = semua.filter(selesai=True)

    stats = semua.aggregate(
    total=Count("id"),
    selesai=Count("id", filter=Q(selesai=True))
    )

    total = stats["total"] or 0
    selesai = stats["selesai"] or 0
    belum = total - selesai
    konsistensi = hitung_konsistensi(total, selesai)

    kategori_stats = semua.values(
        "kategori__nama"
    ).annotate(
        total=Count("id")
    ).order_by("-total")

    # ================= WEEK =================
    week_labels = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
    week_data = OrderedDict({d: 0 for d in week_labels})

    if range_type == "week":
        week_qs = selesai_qs.annotate(
        weekday = ExtractWeekDay('tanggal')
        ).values('weekday').annotate(count=Count('id'))
     
        weekday_map = {
        1: 'Senin',
        2: 'Selasa',
        3: 'Rabu',
        4: 'Kamis',
        5: 'Jumat',
        6: 'Sabtu',
        7: 'Minggu'
        }

        for item in week_qs:
            label = weekday_map.get(item['weekday'])
            if label:
                week_data[label] = item['count']
    
    # ================= MONTH =================
    month_labels = []
    month_values = []

    if range_type == "month":

        today = date.today()
        days = monthrange(today.year, today.month)[1]
        month_data = OrderedDict({d: 0 for d in range(1, days+1)})

        month_qs = (
            selesai_qs
            .annotate(day=ExtractDay("tanggal"))
            .values("day")
            .annotate(total=Count("id"))
        )

        for item in month_qs:
            month_data[item["day"]] = item["total"]

        month_labels = list(month_data.keys())
        month_values = list(month_data.values())

    # ================= ALL =================
    all_labels = []
    all_values = []

    if range_type == "all":

        semua_list = semua.order_by("tanggal")

        if semua_list.exists():

            start = semua_list.first().tanggal.replace(day=1)
            end = date.today().replace(day=1)

            current = start
            all_data = OrderedDict()

            while current <= end:
                label = current.strftime('%b %Y')
                all_data[label] = 0

                if current.month == 12:
                    current = current.replace(year=current.year+1, month=1)
                else:
                    current = current.replace(month=current.month+1)

            all_qs = (
                selesai_qs
                .annotate(
                    month=ExtractMonth("tanggal"),
                    year=ExtractYear("tanggal")
                )
                .values("month", "year")
                .annotate(total=Count("id"))
            )

            for item in all_qs:
                label = date(item["year"], item["month"], 1).strftime('%b %Y')
                if label in all_data:
                    all_data[label] = item["total"]

            all_labels = list(all_data.keys())
            all_values = list(all_data.values())

    # ================= SCALE =================
    if range_type == "week":
        max_value = max(week_data.values()) if week_data else 0
    elif range_type == "month":
        max_value = max(month_values) if month_values else 0
    elif range_type == "all":
        max_value = max(all_values) if all_values else 0
    else:
        max_value = 0

    y_max, step_size = hitung_scale(max_value)
    
    complation_rate = get_completion_rate(user)

    result = {
        "range": range_type,
        "kegiatan": semua,
        "total": total,
        "selesai": selesai,
        "belum": belum,
        "konsistensi": konsistensi,
        "start_period": start_period,
        "end_period": end_period,
        "kategori_stats": kategori_stats,
        "week_labels": list(week_data.keys()),
        "week_values": list(week_data.values()),
        "month_labels": month_labels,
        "month_values": month_values,
        "all_labels": all_labels,
        "all_values": all_values,
        "chart_step": step_size,
        "chart_max": y_max,
        "completion_rate": complation_rate
    }
    
    cache.set(cache_key, result, 300)
    
    return result

def get_completion_rate(user):
    total = Kegiatan.objects.filter(pengguna=user).count()
    
    if total == 0:
        return 0
    
    completed = Kegiatan.objects.filter(pengguna=user, selesai=True).count()
    
    return round((completed / total) * 100)