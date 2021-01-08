from django.shortcuts import render, redirect
from django.contrib.auth import login as do_login, logout as do_logout

from rbac.forms import UserForm, LoginForm


def signup(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            return redirect('/rbac/login')
    else:
        user_form = UserForm()
    return render(request, "signup.html", {'user_form': user_form})


def login(request):
    if request.method == "POST":
        user_form = LoginForm(request.POST)
        if user_form.is_valid():
            do_login(request, user_form.cleaned_data)
            return redirect('/')
    else:
        user_form = LoginForm()
    return render(request, "login.html", {'user_form': user_form})


def logout(request):
    do_logout(request)
    return redirect('/rbac/login')
