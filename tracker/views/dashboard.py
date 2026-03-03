from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from tracker.services.dashboard_service import (
    parse_selected_date,
    get_daily_summary,
    get_date_navigation
)

@login_required(login_url='login')
def dashboard(request):

    date_param = request.GET.get('date')
    filter_param = request.GET.get('filter', 'all')

    selected_date = parse_selected_date(date_param)
    summary = get_daily_summary(request.user, selected_date)

    filtered_qs = summary["queryset"].order_by("waktu")

    if filter_param == "done":
        filtered_qs = filtered_qs.filter(selesai=True)
    elif filter_param == "pending":
        filtered_qs = filtered_qs.filter(selesai=False)

    paginator = Paginator(filtered_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    nav = get_date_navigation(selected_date)

    context = {
        "kegiatan": page_obj,
        "page_obj": page_obj,
        "filter": filter_param,
        "hari_ini": selected_date,
        **summary,
        **nav,
    }

    return render(request, "kegiatan/dashboard.html", context)


@login_required(login_url='login')
def dashboard_total_kegiatan(request):

    selected_date = parse_selected_date(
        request.GET.get("date")
    )

    summary = get_daily_summary(
        request.user,
        selected_date
    )

    return render(
        request,
        "kegiatan/partials/total_kegiatan.html",
        summary
    )