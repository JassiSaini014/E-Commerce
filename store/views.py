from django.shortcuts import render, redirect
from . models import Product, Category, Profile, Customer
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart



def home(request):
    products = Product.objects.all()
    return render(request, 'home.html',{'products':products})

def about(request):
    return render(request, 'about.html',{})

#login function
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)

            current_user = Profile.objects.get(user__id= request.user.id)
            saved_cart = current_user.old_cart
            #convert db string to python dictionary.
            if saved_cart:
                #conver string with JSON.
                converted_cart = json.loads(saved_cart)

                cart = Cart(request)
                for key,value in converted_cart.items():
                    cart.db_add(product=key,quantity=value)

            messages.success(request, "You are logged in successfully...")
            return redirect('home')
        else:
            messages.success(request, "You Must be logged in...")
            return redirect(request, 'login')
    else:
        return render(request, 'login.html',{})

def user_logout(request):
    logout(request)
    messages.success(request, "You are successfully loged out..")
    return redirect('home')


# register user
def register_user(request):
    form = SignUpForm()
    if request.method =='POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #login user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have regisyer successfully, please Update your Info.")
            return redirect('update_info')
        else:
            messages.success(request, "Whoopn there was a problem, Please try again...")
            return redirect('home')

    else:
        return render(request, 'register.html',{'form':form})
    
#product
def product(request, pk):
    products = Product.objects.get(id=pk)
    return render(request, 'product.html',{'products':products})

#Product category
def category(request,foo):
    #replace Hyphen to blank space
    foo = foo.replace('-', ' ')
    #grab the products of same Category
    try:
        #look up the category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {"products":products,'category':category})

    except:
        messages.success(request, "You dont have any Category with this name.")
        return redirect('home')

#update user details

def update_user(request):
    #check if User is logged in.
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('home')
        return render(request, 'update_user.html', {'user_form':user_form})
    else:
        messages.success(request, "Your must be logged in....")
        return redirect('home')

#Update password

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user

        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)

            if form.is_valid():
                form.save()
                messages.success(request, "Your Password has been changed successfully.")
                login(request, current_user)
                return redirect('home')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form':form})
        
    else:
        messages.success(request, "Your must be logged in....")
        return redirect('home')
    

#User info Page
def update_info(request):
    #check if User is logged in.
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, "Your info has been updated successfully.")
            return redirect('home')
        return render(request, 'update_info.html', {'form':form,'shipping_form':shipping_form})
    else:
        messages.success(request, "Your must be logged in....")
        return redirect('home')

    #return render(request, 'update_info.html')


#Search Function.

def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        searched = Product.objects.filter(Q(name__icontains = searched)|Q(description__icontains = searched))
        return render(request, 'search.html', {'searched':searched})
    else:
        return render(request, 'search.html', {})