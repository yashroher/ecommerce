#django libs
from django.contrib import messages
from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

#Verification Libs
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, message
import accounts 

#local libs
from accounts.models import Account
from carts.models import Cart, CartItem
from carts.views import _cart_id
from .forms import RegistrationForm
import requests

# Create your views here.
def register(request):
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name= form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                email = email,
                password = password,
                username = username
            )
            user.phone_number = phone_number
            user.save()
            
            #User Account Verification
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('account/account_verification.html',{
                'user' : user,
                'domain': current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to = [to_email])
            send_email.send()
            return redirect("../login/?command=verification&email="+email)
            
    else: 
        form = RegistrationForm()
    context = {
        'form' : form
    }
    return render(request,"account/register.html",context)

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        
        user = auth.authenticate(email = email,password = password)
        
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart = cart)
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    cart_item_user = CartItem.objects.filter(user = user)
                    exec_variables = []
                    id = []
                    
                    for item in cart_item_user:
                        variation = item.variations.all()
                        exec_variables.append(list(variation))
                        id.append(item.id)
                    
                    for pr in product_variation:
                        if pr in exec_variables:
                            index = exec_variables.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.quantity+=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart = cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request,user)
            messages.success(request,"You are now logged in")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)
            except:
                return redirect("accounts:dashboard")
        else:
            messages.error(request,"Invalid Credentials")
            return redirect("accounts:login")
    return render(request,"account/login.html")

@login_required(login_url = "accounts:login")
def logout(request):
    auth.logout(request)
    return redirect("accounts:login")

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except (TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations! Your Account has been activated')
        return redirect("accounts:login")
    else:
        messages.error("Sorry! wrong activation id")
        return redirect("accounts:register")

@login_required(login_url = "accounts:login")
def dashboard(request):
    return render(request,"account/dashboard.html")

def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email = email).exists():
            user = Account.objects.get(email = email)
            current_site = get_current_site(request)
            mail_subject = "Set New Password"
            message = render_to_string('account/reset_password_email.html',{
                'user' : user,
                'domain': current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to = [to_email])
            send_email.send()
            messages.success(request,"Password resent email has been mailed to you.")
            return redirect("accounts:login")
        else:
            messages.error(request,"No user found!!")
            return redirect("accounts:forgot_password.html")
    return render(request,"account/forgot_password.html")

def reset_password_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except (TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,"Please reset your password")
        return redirect("accounts:reset_password")
    else:
        messages.error(request,"The link has been expired")
        return redirect("accounts:login")
    
def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk = uid)
            user.set_password(password)
            user.save()
            messages.success(request,"You have successfully changed your passord")
            return redirect("accounts:login")
            
        else:
            messages.error(request,"Passwords doesn't match")
            return redirect("accounts:reset_password") 
    return render(request,"account/reset_password.html")