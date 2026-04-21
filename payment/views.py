from django.shortcuts import render, redirect
from cart.cart import Cart
from .forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
from django.contrib import messages
from django.contrib.auth.models import User
from store.models import Product, Profile
import datetime

def orders(request, pk):
     if request.user.is_authenticated and request.user.is_superuser:
          #get the order
          order = Order.objects.get(id=pk)
          #Get the order Items
          items = OrderItem.objects.filter(order=pk)
          #Shipped Status Change Function.
          if request.POST:
               status =request.POST['shipping_status']
               if status == 'true':
                    #grab order
                    order = Order.objects.filter(id=pk)
                    now = datetime.datetime.now()
                    order.update(shipped=True, date_shipped=now)
               else:
                    order = Order.objects.filter(id=pk)
                    order.update(shipped=False)
               messages.success(request,"Shipping status Updated.")
               return redirect('home')


          return render(request, 'payment/orders.html',{'order':order, 'items':items})
     else:
          messages.success(request,'Access Denied')
          return redirect('home')

def not_shipped_dash(request):
     if request.user.is_authenticated and request.user.is_superuser:
          order = Order.objects.filter(shipped=False)
          if request.POST:
               status =request.POST['shipping_status']
               num = request.POST['num']
               order = Order.objects.filter(id=num)
               now = datetime.datetime.now()
               order.update(shipped=True, date_shipped=now)
               messages.success(request,"Shipping status Updated.")
               return redirect('home')


          return render(request, 'payment/not_shipped_dash.html',{'order':order})
     else:
          messages.success(request,'Access Denied')
          return redirect('home') 



def shipped_dash(request):
     if request.user.is_authenticated and request.user.is_superuser:
          order = Order.objects.filter(shipped=True)
          if request.POST:
               status =request.POST['shipping_status']
               num = request.POST['num']
               order = Order.objects.filter(id=num)
               now = datetime.datetime.now()
               order.update(shipped=False)
               messages.success(request,"Shipping status Updated.")
               return redirect('home')

          return render(request, 'payment/shipped_dash.html',{'order':order})
     else:
          messages.success(request,'Access Denied')
          return redirect('home')



def process_order(request):
     if request.POST:
          #get the Cart
          cart = Cart(request)
          cart_products = cart.get_prods
          quantites = cart.get_quants
          totals = cart.cart_total()

          #get billing info form
          payment_form = PaymentForm(request.POST or None)
          #get shipping session Data
          my_shipping = request.session.get('my_shipping')

          #gather order info
          full_name= my_shipping['shipping_full_name']
          email = my_shipping['shipping_email']

          shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
          amount_paid =  totals
          #create order
          if request.user.is_authenticated:
               user = request.user
               #creat order 
               creat_order = Order(user=user,full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
               creat_order.save()

               #Add order items
               #Get order id
               order_id = creat_order.pk
               #get products info
               for product in cart_products():
                    #get product id
                    product_id = product.id
                    #get product price
                    if product.is_sale:
                         price = product.sale_price
                    else:
                         price = product.price

                    #get quantity of products
                    for key, value in quantites().items():
                         if int(key) == product.id:
                              value
                              creat_order_item = OrderItem(order_id=order_id, user=user, product_id=product_id, quantity=value, price=price)
                              creat_order_item.save()
               #delete session
               for key in list(request.session.keys()):
                    if key == "session_key":
                         del request.session[key]

               #delete Cart from Data Base(old_cart field)
               current_user = Profile.objects.filter(user__id=request.user.id)
               #update old_cart
               current_user.update(old_cart="")




               messages.success(request,"Order Placed")
               return redirect('home')
          else:
               creat_order = Order(full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
               creat_order.save()


               order_id = creat_order.pk
               #get products info
               for product in cart_products():
                    #get product id
                    product_id = product.id
                    #get product price
                    if product.is_sale:
                         price = product.sale_price
                    else:
                         price = product.price

                    #get quantity of products
                    for key, value in quantites().items():
                         if int(key) == product.id:
                              value
                              creat_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                              creat_order_item.save()

               #delete session
               for key in list(request.session.keys()):
                    if key == "session_key":
                         del request.session[key]
               messages.success(request,"Order Placed")
               return redirect('home')
     else:
          messages.success(request,"Access Denied")
          return redirect('home')



def billing_info(request):
        if request.POST:
            cart = Cart(request)
            cart_products = cart.get_prods
            quantites = cart.get_quants
            totals = cart.cart_total()

            my_shipping = request.POST
            request.session['my_shipping']= my_shipping



            if request.user.is_authenticated:
                 billing_form = PaymentForm()
                 return render(request, 'payment/billing_info.html',{'cart_products':cart_products, 'quantites':quantites, 'totals':totals,'shipping_info':request.POST,'billing_form':billing_form})
            else:
                 billing_form = PaymentForm()
                 return render(request, 'payment/billing_info.html',{'cart_products':cart_products, 'quantites':quantites, 'totals':totals,'shipping_info':request.POST,'billing_form':billing_form})
            shipping_form = request.POST
            return render(request, 'payment/billing_info.html',{'cart_products':cart_products, 'quantites':quantites, 'totals':totals,'shipping_form':shipping_form})
        else:
            messages.success(request,"Access Denied")
            return redirect('home')
#checkout Function
def checkout(request):
        cart = Cart(request)
        cart_products = cart.get_prods
        quantites = cart.get_quants
        totals = cart.cart_total()

        if request.user.is_authenticated:
             shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
             shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
             return render(request, 'payment/checkout.html',{'cart_products':cart_products, 'quantites':quantites, 'totals':totals,'shipping_form':shipping_form})
             
        else:
            shipping_form = ShippingForm(request.POST or None) 
            return render(request, 'payment/checkout.html',{'cart_products':cart_products, 'quantites':quantites, 'totals':totals,'shipping_form':shipping_form})

def payment_success(request):
    return render(request, "payment/payment_success.html")
