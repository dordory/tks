# apps/territory/manager_views.py
from django.shortcuts import render, redirect, get_object_or_404
from apps.territory.models import Congregation, Territory, Member
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Max, Q
from datetime import datetime, timezone, timedelta


def congregations_view(request):
    congregations = Congregation.objects.all().order_by('name')

    two_months_ago = datetime.now(timezone.utc) - timedelta(days=60)
    for congregation in congregations:
        total_territory_count = Territory.objects.filter(congregation=congregation).count()
        territories_with_last_visit = Territory.objects.filter(congregation=congregation).annotate(last_visited_at=Max("visited_histories__visited_at"))
        old_territory_count = territories_with_last_visit.filter(
            Q(last_visited_at__lt=two_months_ago) | Q(last_visited_at__isnull=True)).count()
        congregation.total_territory_count = total_territory_count
        congregation.old_territory_count = old_territory_count
        if total_territory_count == 0 or old_territory_count == 0:
            congregation.service_coverage = 0
        else:
            congregation.service_coverage = round((1-(old_territory_count / total_territory_count)) * 100, 1)

    return render(request, "manager/congregations.html", {
        "congregations": congregations
    })


def manager_territory_list_view(request, pk):
    congregation = get_object_or_404(Congregation, pk=pk)
    territories = Territory.objects.filter(congregation=congregation).order_by("code")

    # ✅ 최근 방문 정보와 색상 클래스 추가
    now = datetime.now(timezone.utc)
    for territory in territories:
        lv = territory.last_visit()
        territory.last_visit = lv
        if lv and lv.visited_at:
            days_since = (now - lv.visited_at).days
            if days_since >= 60:
                territory.row_class = "bg-red-100"
            else:
                territory.row_class = ""
        else:
            territory.row_class = ""

    # ✅ 페이징
    paginator = Paginator(territories, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ✅ 멤버 목록 (할당용)
    members = Member.objects.all()

    # ✅ 일괄 할당 / 할당 취소 처리
    if request.method == "POST":
        action = request.POST.get("action")
        territory_ids = request.POST.getlist("selected_territories")
        selected_territories = Territory.objects.filter(id__in=territory_ids)

        if action == "assign":
            member_id = request.POST.get("member_id")
            member = get_object_or_404(Member, id=member_id)
            selected_territories.update(assigned_to=member)
            messages.success(request, f"{len(selected_territories)}개 구역이 {member.name}님에게 할당되었습니다.")
        elif action == "unassign":
            selected_territories.update(assigned_to=None)
            messages.success(request, f"{len(selected_territories)}개 구역의 할당이 취소되었습니다.")
        
        return redirect("territory_manager:territory_list", pk=pk)

    return render(request, "manager/territory_list.html", {
        "congregation": congregation,
        "page_obj": page_obj,
        "members": members,
    })