from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from tracker.models import Kategori
from tracker.forms import FormUser

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