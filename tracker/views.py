from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Kategori, Kegiatan
from .forms import FormKegiatan, FormUser
from django.db.models import Count
from calendar import monthrange
from collections import OrderedDict
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator

@login_required(login_url='login')
def profile(request):

    kategori = Kategori.objects.filter(user=request.user)
    edit_id = request.GET.get('edit')

    form_user = FormUser(instance=request.user)
    form_password = PasswordChangeForm(request.user)

    if request.method == 'POST':

        if 'update_user' in request.POST:
          form_user = FormUser(request.POST, instance=request.user)
          if form_user.is_valid():
            form_user.save()
            return redirect('profile')

        elif 'update_password' in request.POST:
          form_password = PasswordChangeForm(request.user, request.POST)
          if form_password.is_valid():
            user = form_password.save()
            update_session_auth_hash(request, user)
            return redirect('profile')

        elif 'edit_kategori' in request.POST:
          kategori_obj = get_object_or_404(
            Kategori,
            id=request.POST.get('id'),
            user=request.user
          )
          nama = request.POST.get('nama')
          if nama:
            kategori_obj.nama = nama
            kategori_obj.save()
          return redirect('profile')

    return render(request, 'kegiatan/profile.html', {
      'kategori': kategori,
      'form_user': form_user,
      'form_password': form_password,
      'edit_id': edit_id
    })

from datetime import date, datetime, timedelta

from datetime import date, datetime, timedelta
from django.core.paginator import Paginator

@login_required(login_url='login')
def dashboard(request):

    today = date.today()

    # ================= DATE PARAM =================
    date_param = request.GET.get('date')
    filter_param = request.GET.get('filter', 'all')

    try:
        selected_date = (
            datetime.strptime(date_param, "%Y-%m-%d").date()
            if date_param else today
        )
    except ValueError:
        selected_date = today

    # ================= BASE QUERY (UNTUK SUMMARY) =================
    base_qs = Kegiatan.objects.filter(
        pengguna=request.user,
        tanggal=selected_date
    )

    total = base_qs.count()
    selesai = base_qs.filter(selesai=True).count()
    belum = total - selesai
    konsistensi = hitung_konsistensi(total, selesai)

    # ================= FILTER UNTUK LIST =================
    filtered_qs = base_qs.order_by('waktu')

    if filter_param == 'done':
        filtered_qs = filtered_qs.filter(selesai=True)
    elif filter_param == 'pending':
        filtered_qs = filtered_qs.filter(selesai=False)

    # ================= PAGINATION =================
    paginator = Paginator(filtered_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ================= NAVIGATION =================
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    context = {
        'kegiatan': page_obj,
        'page_obj': page_obj,
        'total': total,
        'selesai': selesai,
        'belum': belum,
        'konsistensi': konsistensi,
        'hari_ini': selected_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'today': today,
        'filter': filter_param,
    }

    return render(request, 'kegiatan/dashboard.html', context)
  
@login_required(login_url='login')
def dashboard_total_kegiatan(request):

    date_param = request.GET.get("date")
    today = date.today()

    try:
        selected_date = (
            datetime.strptime(date_param, "%Y-%m-%d").date()
            if date_param else today
        )
    except ValueError:
        selected_date = today

    base_qs = Kegiatan.objects.filter(
        pengguna=request.user,
        tanggal=selected_date
    )

    total = base_qs.count()
    selesai = base_qs.filter(selesai=True).count()
    belum = total - selesai
    konsistensi = hitung_konsistensi(total, selesai)

    return render(
        request,
        "kegiatan/partials/total_kegiatan.html",
        {
            "total": total,
            "selesai": selesai,
            "belum": belum,
            "konsistensi": konsistensi,
        }
    )

@login_required(login_url='login')
def semua_kegiatan(request):
  kegiatan = Kegiatan.objects.filter(
    pengguna=request.user
  )
  
  filter_type = request.GET.get('filter')
  today = date.today()
  
  if filter_type == 'today':
    kegiatan = kegiatan.filter(tanggal=today)
      
  elif filter_type == 'week':
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)
    kegiatan = kegiatan.filter(tanggal__range=[start_week, end_week])
      
  elif filter_type == 'done':
    kegiatan = kegiatan.filter(selesai=True)
      
  elif filter_type == 'pending':
    kegiatan = kegiatan.filter(selesai=False)
  kegiatan = kegiatan.order_by('-tanggal', '-waktu')
  
  return render(request, 'kegiatan/semua.html', {
    'kegiatan': kegiatan,
    'filter': filter_type
  })

@login_required(login_url='login')
def tambah_kegiatan(request):

    if request.method == 'POST':
        form = FormKegiatan(request.POST, user=request.user)

        if form.is_valid():
            data = form.save(commit=False)
            data.pengguna = request.user

            tanggal_post = request.POST.get('tanggal')
            if tanggal_post:
                data.tanggal = tanggal_post

            data.save()

            # Redirect ke dashboard dengan tanggal yang sama
            if tanggal_post:
                return redirect(f"{reverse('dashboard')}?date={tanggal_post}")

            return redirect('dashboard')

    else:
        form = FormKegiatan(user=request.user)

    return render(request, 'kegiatan/tambah.html', {'form': form})

@login_required(login_url='login')
def edit_kegiatan(request, id):

  kegiatan = get_object_or_404(
    Kegiatan,
    id=id,
    pengguna=request.user
  )

  if request.method == 'POST':
    form = FormKegiatan(
      request.POST,
      instance=kegiatan,
      user=request.user
    )
    if form.is_valid():
      form.save()
      return redirect('semua_kegiatan')
  else:
    form = FormKegiatan(
      instance=kegiatan,
      user=request.user
    )

  return render(request, 'kegiatan/edit.html', {
    'form': form
  })

@login_required(login_url='login')
def hapus_kegiatan(request, id):
  kegiatan = get_object_or_404(
    Kegiatan,
    id=id,
    pengguna=request.user
  )
  kegiatan.delete()
  return redirect('semua_kegiatan')

@require_POST
@login_required(login_url='login')
def toggle_selesai(request, id):

    kegiatan = get_object_or_404(
        Kegiatan,
        id=id,
        pengguna=request.user
    )

    kegiatan.selesai = not kegiatan.selesai
    kegiatan.save()

    if request.headers.get("HX-Request"):

        # hitung ulang summary hari ini
        selected_date = kegiatan.tanggal

        base_qs = Kegiatan.objects.filter(
            pengguna=request.user,
            tanggal=selected_date
        )

        total = base_qs.count()
        selesai = base_qs.filter(selesai=True).count()
        belum = total - selesai
        konsistensi = hitung_konsistensi(total, selesai)

        response = render(
            request,
            "kegiatan/partials/task_item.html",
            {"item": kegiatan}
        )

        response["HX-Trigger"] = "summaryUpdated"

        return response

    return redirect("dashboard")

def hitung_konsistensi(total, selesai):
  if total == 0:
    return 0
  return int((selesai / total) * 100)

def hitung_scale(max_value):
    step = 5

    if max_value <= 20:
        y_max = 20
    else:
        import math
        y_max = math.ceil(max_value / step) * step

    return y_max, step

@login_required(login_url='login')
def analytics(request):
    today = date.today()
    range_type = request.GET.get('range', 'week')

    semua = Kegiatan.objects.filter(pengguna=request.user)

    if range_type == 'week':
        start_period = today - timedelta(days=today.weekday())
        end_period = start_period + timedelta(days=6)

    elif range_type == 'month':
        start_period = today.replace(day=1)
        last_day = monthrange(today.year, today.month)[1]
        end_period = today.replace(day=last_day)

    else:
        first = semua.order_by('tanggal').first()
        last = semua.order_by('-tanggal').first()
        start_period = first.tanggal if first else today
        end_period = last.tanggal if last else today

    semua = semua.filter(tanggal__range=[start_period, end_period]).order_by('tanggal','waktu')

    selesai_qs = semua.filter(selesai=True)

    total = semua.count()
    selesai = selesai_qs.count()
    belum = total - selesai
    konsistensi = hitung_konsistensi(total, selesai)

    kategori_stats = semua.values(
        'kategori__nama'
    ).annotate(
        total=Count('id')
    ).order_by('-total')

    week_labels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    week_data = OrderedDict({d:0 for d in week_labels})

    if range_type == 'week':
        for k in selesai_qs:
            day = k.tanggal.strftime('%a')
            if day in week_data:
                week_data[day] += 1

    month_labels = []
    month_values = []

    if range_type == 'month':
        days = monthrange(today.year, today.month)[1]
        month_data = OrderedDict({d:0 for d in range(1, days+1)})

        for k in selesai_qs:
            day = k.tanggal.day
            if day in month_data:
                month_data[day] += 1

        month_labels = list(month_data.keys())
        month_values = list(month_data.values())
        
    all_labels = []
    all_values = []

    if range_type == 'all':

        semua_list = semua.order_by('tanggal')  # pakai semua, bukan selesai

        if semua_list.exists():

            start = semua_list.first().tanggal.replace(day=1)
            end = today.replace(day=1)

            current = start
            all_data = OrderedDict()

            while current <= end:
                label = current.strftime('%b %Y')
                all_data[label] = 0

                # pindah ke bulan berikutnya
                if current.month == 12:
                    current = current.replace(year=current.year+1, month=1)
                else:
                    current = current.replace(month=current.month+1)

            # isi hanya task selesai
            for k in selesai_qs:
                label = k.tanggal.strftime('%b %Y')
                if label in all_data:
                    all_data[label] += 1

            all_labels = list(all_data.keys())
            all_values = list(all_data.values())

    if range_type == 'week':
        max_value = max(week_data.values()) if week_data else 0
    elif range_type == 'month':
        max_value = max(month_values) if month_values else 0
    elif range_type == 'all':
        max_value = max(all_values) if all_values else 0
    else:
        max_value = 0

    y_max, step_size = hitung_scale(max_value)

    context = {
        'range': range_type,
        'kegiatan': semua,
        'total': total,
        'selesai': selesai,
        'belum': belum,
        'konsistensi': konsistensi,
        'start_period': start_period,
        'end_period': end_period,
        'kategori_stats': kategori_stats,
        'week_labels': list(week_data.keys()),
        'week_values': list(week_data.values()),
        'month_labels': month_labels,
        'month_values': month_values,
        'chart_step': step_size,
        'chart_max': y_max,
        'all_labels': all_labels,
        'all_values': all_values,
    }

    return render(request, 'kegiatan/analytics.html', context)

@login_required(login_url='login')
def tambah_kategori(request):

  if request.method == 'POST':
    nama = request.POST.get('nama')

    if nama:
      Kategori.objects.create(
        user=request.user,
        nama=nama
      )

  return redirect('profile')
  
@login_required(login_url='login')
def edit_kategori(request, id):

  kategori = get_object_or_404(
    Kategori,
    id=id,
    user=request.user
  )

  if request.method == 'POST':
    nama = request.POST.get('nama')

    if nama:
      kategori.nama = nama
      kategori.save()

  return redirect('profile')
  
@login_required(login_url='login')
def hapus_kategori(request, id):

  kategori = get_object_or_404(
    Kategori,
    id=id,
    user=request.user
  )

  kategori.delete()
  return redirect('profile')