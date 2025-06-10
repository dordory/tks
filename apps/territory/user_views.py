from django.core.paginator import Paginator
from django.utils import timezone
from django.shortcuts import render, redirect,  get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from zoneinfo import ZoneInfo
from django.views.decorators.http import require_POST
from datetime import timedelta, datetime

from .models import Territory, VisitHistory, Congregation, TerritoryCategory
from apps.member.models import Member, Group
from .forms import VisitHistoryForm, TerritoryNoteForm
from .forms import InlineVisitHistoryForm  # 이 폼을 따로 만들어야 합니다


@require_POST
def update_territory_info(request, territory_id):
    territory = get_object_or_404(Territory, pk=territory_id)
    member_id = request.session.get('member_id')

    if not member_id or territory.assigned_to_id != int(member_id):
        messages.error(request, "정보를 변경할 수 없습니다.")
        return redirect('territory:user_assigned_territories')

    # 카테고리 변경
    category_id = request.POST.get("category")
    if category_id:
        try:
            category = TerritoryCategory.objects.get(id=category_id)
            territory.category = category
        except TerritoryCategory.DoesNotExist:
            messages.error(request, "유효하지 않은 카테고리입니다.")

    # 노트 변경
    note = request.POST.get("note", "").strip()
    territory.note = note
    

    territory.save()
    messages.success(request, "구역 정보가 업데이트되었습니다.")
    return redirect('territory:user_territory_detail', territory_id=territory.id)


def user_groups_view(request):
    groups = Group.objects.filter(active=True)
    return render(request, "user_groups.html", {"groups": groups})


def user_login_view(request):
    group_id = request.GET.get("group_id")
    if group_id:
        members = Member.objects.filter(group_id=group_id)
        return render(request, "territory/login.html", {
            "members": members,
            "group_id": group_id
        })
    else:
        return redirect(reverse("territory:user_groups"))


def user_assigned_territories(request, member_id):
    if not member_id:
        return redirect('territory:user_login')

    territories = Territory.objects.filter(
        assigned_to_id=member_id
    ).annotate(
        last_visited_at=Max("visited_histories__visited_at")
    ).order_by("last_visited_at")

    today = datetime.now().date()

    for territory in territories:
        if territory.last_visit:
            territory.last_visited_status = territory.last_visit().status
            territory.last_visited_at = territory.last_visit().visited_at.astimezone(ZoneInfo("Asia/Tokyo"))
            delta_days = (today - territory.last_visit().visited_at.date()).days
            if territory.last_visit().visited_at.date() == today:
                territory.visit_status = "today"
            elif delta_days >= 60:
                territory.visit_status = "old"
            elif delta_days >= 30:
                territory.visit_status = "warning"
            else:
                territory.visit_status = "normal"
        else:
            territory.last_visited_status = None
            territory.last_visited_at = None
            territory.visit_status = "none"

    return render(request, 'territory/user_assigned_territories.html', {
        'territories': territories,
        'member_id': member_id,
    })


def user_territory_detail(request, member_id, territory_id):
    #member_id = request.session.get('member_id')
    #member_id = request.GET.get('member_id')
    #territory_id = request.GET.get('territory_id')

    if not member_id:
        return redirect('territory:user_login')

    territory = get_object_or_404(Territory, id=territory_id, assigned_to_id=member_id)
    visits = VisitHistory.objects.filter(territory=territory).order_by('-visited_at')
    categories = TerritoryCategory.objects.all()

    if request.method == "POST":
        form = InlineVisitHistoryForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.territory = territory
            visit.visitor = territory.assigned_to if territory.assigned_to else get_object_or_404(Member, pk=1)

            visit.visited_at = timezone.now()
            visit.save()
            messages.success(request, "방문기록이 추가되었습니다")
            return redirect('territory:user_territory_detail', member_id=member_id, territory_id=territory_id)
    else:
        form = InlineVisitHistoryForm()

    return render(request, 'territory/user_territory_detail.html', {
        'member_id': member_id,
        'territory': territory,
        'visits': visits,
        'categories': categories,
        'form': form,
    })

def user_territory_list_view(request, member_id):
    member = Member.objects.get(pk=member_id)
    territories = Territory.objects.filter(assigned_to=member)
    return render(request, 'territory/territories_by_congregation.html', {
        'territories': territories,
        'member': member
    })


def select_member_view(request):
    members = Members.objects.all()
    return render(request, "manager/select_congregation.html", {
        "congregations": congregations
    })


@require_POST
def update_territory_note(request, territory_id):
    territory = get_object_or_404(Territory, pk=territory_id)
    territory.note = request.POST.get("note", "").strip()
    territory.save()
    return redirect('territory:territory_detail_from_congregation', congregation_id=territory.congregation_id, territory_id=territory.id)


def congregation_list_view(request):
    congregations = Congregation.objects.all().order_by("num")

    two_months_ago = timezone.now() - timedelta(days=60)
    for congregation in congregations:
        total_territory_count = Territory.objects.filter(congregation=congregation). count()
        territories_with_last_visit = Territory.objects.filter(congregation=congregation).annotate(last_visited_at=Max("visited_histories__visited_at"))
        old_territory_count = territories_with_last_visit.filter(
            Q(last_visited_at__lt=two_months_ago) | Q(last_visited_at__isnull=True)).count()
        congregation.total_territory_count = total_territory_count
        congregation.old_territory_count = old_territory_count
        if total_territory_count == 0 or old_territory_count == 0:
            congregation.service_coverage = 0
        else:
            congregation.service_coverage = round((1-(old_territory_count / total_territory_count)) * 100, 1)

    return render(request, "territory/congregation_list.html", {"congregations": congregations})


def territories_by_congregation_view(request, pk):
    congregation = get_object_or_404(Congregation, pk=pk)
    territories = Territory.objects.filter(congregation=congregation).annotate(last_visited_at=Max("visited_histories__visited_at"))

    cutoff = timezone.now() - timedelta(days=60)
    for territory in territories:
        last_visit = territory.last_visit()
        territory.last_visited_at = last_visit.visited_at if last_visit else None
        territory.is_old = territory.last_visited_at and territory.last_visited_at < cutoff

    return render(request, "territory/territories_by_congregation.html", {
        "congregation": congregation,
        "territories": territories
    })


def territory_detail_from_congregation(request, congregation_id, territory_id):
    territory = get_object_or_404(Territory, id=territory_id, congregation_id=congregation_id)
    visits = VisitHistory.objects.filter(territory=territory).order_by('-visited_at')

    if request.method == "POST":
        form = InlineVisitHistoryForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.territory = territory
            visit.visitor = territory.assigned_to if territory.assigned_to else get_object_or_404(Member, pk=1)

            visit.visited_at = timezone.now()
            visit.save()
            return redirect('territory:territory_detail_from_congregation', congregation_id=congregation_id, territory_id=territory_id)
    else:
        form = InlineVisitHistoryForm()

    return render(request, 'territory/territory_detail_from_congregation.html', {
        'territory': territory,
        'visits': visits,
        'form': form,
    })


@login_required
def territory_list(request):
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 20

    territory_list = Territory.objects.all().order_by("code")

    paginator = Paginator(territory_list, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "territory/list.html", {
        'page_obj': page_obj,
        'per_page': per_page,
    })


@login_required
def territory_detail_view(request, pk):
    territory = get_object_or_404(Territory, pk=pk)
    visit_histories = VisitHistory.objects.filter(territory=territory).select_related("visitor", "status").order_by("-visited_at")
    return render(request, "territory/detail.html", {
        "territory": territory,
        "visit_histories": visit_histories,
    })


@login_required
def visit_history_create_view(request, territory_id):
    territory = get_object_or_404(Territory, id=territory_id)

    if request.method == 'POST':
        visit_form = VisitHistoryForm(request.POST)
        note_form = TerritoryNoteForm(request.POST, instance=territory)
        
        if visit_form.is_valid() and note_form.is_valid():
            visit = visit_form.save(commit=False)
            print("visit.visited_at: ", visit.visited_at)
            visit.territory = territory
            visit.save()
            note_form.save()
            return redirect('territory:territory_detail', pk=territory.id)
    else:
        visit_form = VisitHistoryForm()
        note_form = TerritoryNoteForm(instance=territory)

    return render(request, 'territory/visit_history_form.html', {
        'visit_form': visit_form,
        'note_form': note_form,
        'territory': territory,
    })