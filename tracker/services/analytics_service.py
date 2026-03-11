from datetime import date, timedelta
from calendar import monthrange
from collections import OrderedDict
from django.db.models import Count, Q, Max, Min
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
        range_data = semua.aggregate(
            first_date = Min("tanggal"),
            last_date = Max("tanggal")
        )
        start = range_data["first_date"] or today
        end = range_data["last_date"] or today

    return start, end

def hitung_streak(user):
    today = date.today()
    
    tanggal_selesai = (
        Kegiatan.objects.filter(
           pengguna = user,
           selesai = True, 
           tanggal__lte = date.today()
        )
        .values_list("tanggal", flat=True)
        .distinct()
        .order_by("-tanggal")
    )
    
    streak = 0
    current_day = today
    
    for tgl in tanggal_selesai:
        if tgl == current_day:
            streak += 1
            current_day = current_day - timedelta(days=1)
        elif tgl < current_day:
            break
    return streak

def hitung_longest_streak(user):
    tanggal_selesai = (
        Kegiatan.objects.filter(
            pengguna = user,
            selesai =True,
        )
        .values_list("tanggal", flat=True)
        .distinct()
        .order_by("tanggal")
    )
    
    tanggal_list = list(tanggal_selesai)
    
    if not tanggal_list:
        return 0
    
    longest = 1
    current = 1
    
    for i in range (1, len(tanggal_list)):
        if tanggal_list[i] == tanggal_list[i-1] + timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1
            
    return longest

def build_analytics_data(user, range_type):    
    cache_key = f"analytics_{user.id}_{range_type}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        print("Mengambil data dari cache")
        return cached_data
    print("Mengambil data dari database")

    start_period, end_period = get_period_range(user, range_type)

    kegiatan_qs = (
        Kegiatan.objects
        .filter(
            pengguna=user,
            tanggal__range=(start_period, end_period)
        )
    )
    selesai_qs = kegiatan_qs.filter(selesai=True)

    stats = kegiatan_qs.aggregate(
        total=Count("id"),
        selesai=Count("id", filter=Q(selesai=True))
    )

    total = stats["total"] or 0
    selesai = stats["selesai"] or 0
    belum = total - selesai
    konsistensi = hitung_konsistensi(total, selesai)

    kategori_stats = kegiatan_qs.values(
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

        semua_list = kegiatan_qs.order_by("tanggal")
        
        first_item = semua_list.first()

        if first_item:

            start = first_item.tanggal.replace(day=1)
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
    
    if total > 0:
        completion_rate = round((selesai / total) * 100)
    else:
        completion_rate = 0
        
    streak = hitung_streak(user)
    longest = hitung_longest_streak(user)

    result = {
        "range": range_type,
        "kegiatan": kegiatan_qs,
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
        "completion_rate": completion_rate,
        "streak": streak,
        "longest_streak": longest,
    }
    
    cache.set(cache_key, result, 300)
    
    return result