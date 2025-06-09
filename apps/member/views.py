from django.shortcuts import render
from .models import Member


# Create your views here.
def user_list_view(request):
    members = Member.objects.filter(active=True).order_by('group', 'name')
    return render(request, "member/user_list.html", {"members": members})