from django.shortcuts import render, redirect, get_object_or_404

from .forms import BlogForm
from .models import *
# Create your views here.
def posts(request):
    queryset=Blog.objects.all()
    filtered=[]
    cu=CustomUser.objects.filter(id=request.user.id).first()
    for blog in queryset:
        if blog.user not in cu.blocked_users.all():
            filtered.append(blog)
        elif request.user not in blog.user.blocked_users.all():
            filtered.append(blog)
        elif request.user!=blog.user:
            filtered.append(blog)
    context = {"blogs":filtered}
    return render(request, "posts.html", context=context)

def profile(request):
    queryset = Blog.objects.all()
    filtered = []
    for blog in queryset:
        if request.user == blog.user:
            filtered.append(blog)
    context = {"blogs": filtered,"user":request.user}
    return render(request, "profile.html", context=context)

def add_post(request):
    if request.method == "POST":
        form_data = BlogForm(data=request.POST,files=request.FILES)
        if form_data.is_valid():
            blog = form_data.save(commit=False)
            blog.user = request.user
            blog.save()
            return redirect("profile")

    return render(request, "add.html", context={"form": BlogForm})


def blocked(request):

    user=CustomUser.objects.filter(id=request.user.id).first()
    users=CustomUser.objects.exclude(id=user.id).all()
    filtered=[]
    for user1 in users:
        if user1 not in user.blocked_users.all():
            filtered.append(user1)
    if request.method == "POST" and request.POST.get('action')!='delete':
        id=request.POST.get('userid')
        user.blocked_users.add(CustomUser.objects.filter(id=int(id)).first())
        return redirect("profile")
    elif request.method == "POST":
        id = request.POST.get('userid')
        user.blocked_users.remove(CustomUser.objects.filter(id=int(id)).first())
        return redirect("blocked")
    return render(request, "blocked.html", context={"users":filtered,"blocked":user.blocked_users.all(),"user":request.user})
