from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Service
from .forms import ServiceForm

@staff_member_required
def service_admin_list(request):
    q = request.GET.get("q", "")
    services = Service.objects.all().order_by("-id")
    if q:
        services = services.filter(name__icontains=q)
    return render(request, "adminx/service_list.html", {"services": services, "q": q})

@staff_member_required
def service_admin_create(request):
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มบริการเรียบร้อย")
            return redirect("admin_service_list")
    else:
        form = ServiceForm()
    return render(request, "adminx/service_form.html", {"form": form, "mode": "create"})

@staff_member_required
def service_admin_update(request, pk):
    obj = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "บันทึกการแก้ไขแล้ว")
            return redirect("admin_service_list")
    else:
        form = ServiceForm(instance=obj)
    return render(request, "adminx/service_form.html", {"form": form, "mode": "edit", "obj": obj})

@staff_member_required
def service_admin_delete(request, pk):
    obj = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "ลบบริการแล้ว")
        return redirect("admin_service_list")
    return render(request, "adminx/service_delete_confirm.html", {"obj": obj})
