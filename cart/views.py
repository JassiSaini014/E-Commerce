from django.shortcuts import render, get_object_or_404, redirect
from.cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

def cart_summary(request):
		cart = Cart(request)
		cart_products = cart.get_prods
		quantites = cart.get_quants
		totals = cart.cart_total()
		return render(request, 'cart_summary.html',{'cart_products':cart_products, 'quantites':quantites, 'totals':totals})


def cart_add(request):
	# Get the cart
	cart = Cart(request)
	# test for POST
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))
		# lookup product in DB
		product = get_object_or_404(Product, id=product_id)
		# Save to session
		cart.add(product=product, quantity=product_qty)
        #cart quantity
		cart_quantity = cart.__len__()
		# Return resonse
		response = JsonResponse({'qty: ': cart_quantity})
		messages.success(request, ("Product Added To Cart..."))
		return response

#cart delete function
def cart_delete(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		# delete fuction for perticular Product.
		cart.delete(product=product_id)

		response = JsonResponse({'product':product_id})
		messages.success(request, ("Product has been deleted.."))
		return response




#cart Update Function
def cart_update(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))

		cart.update(product=product_id, quantity=product_qty)
		response = JsonResponse({'qty':product_qty})
		messages.success(request, ("Changes has been successfully applied."))	
		return response
