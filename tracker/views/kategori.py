from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from tracker.models import Kategori


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