from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from tracker.services.analytics_service import build_analytics_data

@login_required(login_url='login')
def analytics(request):
    range_type = request.GET.get("range", "week")

    data = build_analytics_data(
        request.user,
        range_type
    )

    return render(
        request,
        "kegiatan/analytics.html",
        data
    )