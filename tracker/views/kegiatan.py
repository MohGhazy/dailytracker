from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from tracker.models import Kegiatan
from tracker.forms import FormKegiatan
from tracker.services.kegiatan_service import get_filtered_kegiatan, toggle_kegiatan_status, create_kegiatan, update_kegiatan, delete_kegiatan, get_kegiatan
from django.core.paginator import Paginator

@login_required(login_url='login')
def semua_kegiatan(request):
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get("q", "")

    kegiatan = get_filtered_kegiatan(
        user=request.user,
        filter_type=filter_type,
        search_query=search_query,
    )

    page_number = request.GET.get("page")
    paginator = Paginator(kegiatan, 5)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'kegiatan/kegiatan.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'filter': filter_type,
        'search_query': search_query,
    })

@login_required(login_url='login')
def tambah_kegiatan(request):

    if request.method == 'POST':
        form = FormKegiatan(request.POST, user=request.user)

        if form.is_valid():
            kegiatan = create_kegiatan(
                request.user,
                form
            )
            
            return redirect(f"{reverse('dashboard')}?date={kegiatan.tanggal}")

    else:
        form = FormKegiatan(user=request.user)

    return render(request, 'kegiatan/tambah.html', {'form': form})

@login_required(login_url='login')
def edit_kegiatan(request, id):

    kegiatan = get_kegiatan(request.user, id)

    if request.method == 'POST':
        form = FormKegiatan(
            request.POST,
            instance=kegiatan,
            user=request.user
        )

        if form.is_valid():
            update_kegiatan(kegiatan, form)
            return redirect('semua_kegiatan')
    else:
        form = FormKegiatan(
            instance=kegiatan,
            user=request.user
        )

    return render(request, 'kegiatan/edit.html', {
        'form': form
    })

@require_POST
@login_required(login_url='login')
def hapus_kegiatan(request, id):
    delete_kegiatan(request.user, id)
    return redirect('semua_kegiatan')

@require_POST
@login_required(login_url='login')
def toggle_selesai(request, id):
    kegiatan = toggle_kegiatan_status(
        user=request.user,
        kegiatan_id=id
    )

    if request.headers.get("HX-Request"):
        response = render(
            request,
            "kegiatan/partials/task_item.html",
            {"item": kegiatan}
        )
        response["HX-Trigger"] = "summaryUpdated"
        return response

    return redirect("dashboard")