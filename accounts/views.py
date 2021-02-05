from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from . import forms
from . models import Customer

def signup_view(request):
    statement = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        custForm = forms.CustomerForm(request.POST)
        if form.is_valid():
            if custForm.is_valid():
                    user = form.save(commit=False)                
                    instance = Customer()
                    instance.email = custForm.cleaned_data.get('email')
                    instance.firstName = custForm.cleaned_data.get('firstName')
                    instance.lastName = custForm.cleaned_data.get('lastName')
                    instance.street = custForm.cleaned_data.get('street')
                    instance.city = custForm.cleaned_data.get('city')
                    instance.state = custForm.cleaned_data.get('state')                
                    instance.zipcode = custForm.cleaned_data.get('zipcode')
                    instance.phoneNumber = custForm.cleaned_data.get('phoneNumber')
                    instance.verified = 'UnVerified'
                    instance.user = user
                    user = form.save()                                    
                    instance.save()
                    login(request, user)
                    return redirect('fitnessClass:schedule')
    else:
        form = UserCreationForm()
        custForm = forms.CustomerForm()
    return render(request, 'accounts/signup.html', { 'form': form, 'customerForm': custForm , 'statement':statement })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
               return redirect('fitnessClass:schedule')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', { 'form': form })

def logout_view(request):
    if request.method == 'GET':
        logout(request)
        form = AuthenticationForm
        return render(request, 'accounts/login.html', {'form':form})