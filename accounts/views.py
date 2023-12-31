from multiprocessing import allow_connection_pickling
from django.shortcuts import render, redirect
from django.http import HttpResponse, request
from matplotlib.style import context
from accounts.decorators import unauthenticated_user
from accounts.forms import OrderForm
from .forms import OrderForm, CreateUserForm
from accounts.models import Customer, Product, Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate,login,logout
from .decorators import admin_only, unauthenticated_user, allowed_users, admin_only
@unauthenticated_user
def registerPage(request):
    
    form=CreateUserForm()
    if request.method == "POST":
        form= CreateUserForm(request.POST)
        if form.is_valid():
            user=form.save()
            username=form.cleaned_data.get('username')
            group=Group.objects.get(name="customer")
            user.groups.add(group)
            Customer.objects.create(
                user=user,
                name=user.username
            )
            messages.success(request, 'Acoount was created for '+username)
            return redirect('login')    

    context={'form':form}
    return render(request,'accounts/register.html',context)    


def loginPage(request):
    

    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(request, username= username, password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Username OR Password is incorrect')

    context={}
    return render(request,'accounts/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
#@admin_only
def home(request):
    orders = Order.objects.all()
    customer = Customer.objects.all()
    total_customers=customer.count()
    total_orders=orders.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='Pending').count()
    context = {'orders':orders, 'customers':customer, 'total_orders':total_orders,'delivered':delivered,'pending':pending}
    return render(request,'accounts/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders=request.user.customer.order_set.all()
    total_orders=orders.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='Pending').count()
    print('ORDERS:',orders)
    context={'orders':orders, 'customers':customer, 'total_orders':total_orders,'delivered':delivered,'pending':pending}
    return render(request, 'accounts/user.html',context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product(request):
    products=Product.objects.all()
    return render(request,'accounts/product.html',{'products':products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders=customer.order_set.all()
    order_count=orders.count()
    context={'customer':customer,'orders':orders,'order_count':order_count,}
    return render(request,'accounts/customer.html',context)

def createorder(request):
    form=OrderForm
    if request.method=='POST':
        #print('Printing POST:',request.POST)
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    context={'form':form}
    return render(request, 'accounts/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form= OrderForm(instance=order)
    if request.method=='POST':
        #print('Printing POST:',request.POST)
        form = OrderForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context={'form':form}
    return render(request, 'accounts/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect('/')
    context={'item':order}
    return render(request,'accounts/delete.html',context)