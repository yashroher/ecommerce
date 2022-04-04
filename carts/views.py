from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import Cart,CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    product = Product.objects.get(id = product_id)
    current_user = request.user
    
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for items in request.POST:
                key = items 
                value = request.POST[key]
                print(key,value)
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()

        cart_exist = CartItem.objects.filter(product=product,user = current_user).exists()

        if cart_exist:
            cart_item = CartItem.objects.filter(product=product,user=current_user)
            ids = []
            ex_var = []
            for item in cart_item:
                existing_variable = item.variations.all()
                ex_var.append(list(existing_variable))
                ids.append(item.id)
            print(ex_var)
            if product_variation in ex_var:
                idex = ex_var.index(product_variation)
                item_id = ids[idex]
                item = CartItem.objects.get(product=product,id = item_id)
                item.quantity+=1
                item.save()
            else:
                item = CartItem.objects.create(product = product,user = current_user,quantity = 1)
                if(len(product_variation)>0):
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                user = current_user, 
                quantity =1 ,
            )
            if(len(product_variation)>0):
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        
        return redirect('/cart')
    else:
        product_variation = []
        if request.method == 'POST':
            for items in request.POST:
                key = items 
                value = request.POST[key]
                print(key,value)
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                    print("This is",product_variation)
                except:
                    print("problem")
                    pass
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()

        cart_exist = CartItem.objects.filter(product=product,cart=cart).exists()

        if cart_exist:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            ids = []
            ex_var = []
            for item in cart_item:
                existing_variable = item.variations.all()
                ex_var.append(list(existing_variable))
                ids.append(item.id)
            print(ex_var)
            if product_variation in ex_var:
                idex = ex_var.index(product_variation)
                item_id = ids[idex]
                item = CartItem.objects.get(product=product,id = item_id)
                item.quantity+=1
                item.save()
            else:
                item = CartItem.objects.create(product = product,cart = cart,quantity = 1)
                if(len(product_variation)>0):
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                cart = cart,
                quantity =1 ,
            )
            if(len(product_variation)>0):
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        
        return redirect('/cart')

def increment(request,cart_item_id):
    try:
        cart_item = CartItem.objects.get(id = cart_item_id)
        cart_item.quantity+=1
        cart_item.save()
    except:
        pass
    return redirect("/cart")

def remove_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id = product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product,user = request.user,id = cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request)) 
            cart_item = CartItem.objects.get(product = product,cart = cart,id = cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect("cart:cart")

def remove_cart_item(request,product_id,cart_item_id):
    try:
        product = get_object_or_404(Product,id = product_id)
        if request.user.is_authenticated:
           cart_item = CartItem.objects.get(product = product,user = request.user,id = cart_item_id)
        else: 
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product = product,cart = cart,id = cart_item_id)
        cart_item.delete()
    except:
        pass
    return redirect("cart:cart")

def cart(request):
    total = 0
    quantity = 0
    cart_items = None
    grant_total,tax = 0,0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user,is_active = True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = 2*total/100
        grant_total = total+tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grant_total
    }
    return render(request,'store/cart.html',context)

@login_required(login_url='accounts:login')
def checkout(request):
    total = 0
    quantity = 0
    cart_items = None
    grant_total,tax = 0,0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user,is_active = True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = 2*total/100
        grant_total = total+tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grant_total
    }
    return render(request,"store/checkout.html",context)