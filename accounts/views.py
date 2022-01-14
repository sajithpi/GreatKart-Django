from django import forms
from django.contrib import messages,auth
from django.shortcuts import redirect, render
from django.utils import http
from django.http import HttpResponse
from accounts.models import Account
from carts.models import Cart, CartItem
from carts.views import get_cart_id

from .forms import RegistrationForm
#verification email
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, message
import requests
# Create your views here.

def register(request):
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = email,
               
                password = password,

            )
            user.phone_number = phone_number
            user.save()
            #USER ACTIVATION

            current_site = get_current_site(request)
            mail_subject = 'Please Activate Your Account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),



            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()


            # messages.success(request,"Thankyou for registering with us, We have sent you a verification email to your email address. Please verify it.")
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()    
    context = {
            'form' : form,
    }
    return render(request,'accounts/register.html',context)
   
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)
    
        if user is not None:
            try:
                print("enterting try block")
                cart = Cart.objects.get(cart_id = get_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                print(is_cart_item_exists)
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)


                    #getting product variations by Id

                    product_variation = []
                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))

                    #Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user = user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr_var in product_variation:
                        if pr_var in ex_var_list:
                            index = ex_var_list.index(pr_var)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:

                            cart_item = CartItem.objects.filter(cart = cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                print("entering pass block")

            auth.login(request,user)
            messages.success(request,"Login Successfully")
            url = request.META.get('HTTP_REFERER')
            print("url:",url)
            try:
                 query = requests.utils.urlparse(url).query
                #  print('query ->',query)
                 params = dict(x.split('=') for x in query.split('&'))
                #  print('params -> ',params)
                 if 'next' in params:
                     urlpath = params['next']
                    #  print('next:',urlpath)
                     return redirect('/cart/checkout/')
               
            except:
               
                return redirect('accounts:dashboard')
            
            # except:
            #     pass
        else:
            messages.error(request,"Invalid user credentials")
            return redirect('accounts:login')
    return render(request,'accounts/login.html')

@login_required(login_url = 'accounts:login')
def logout(request):
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('accounts:login')

def activate(request,uidb64,token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations, Your Account has been activated')
        return redirect('accounts:login')
    else:
        messages.error(request,"Invalid activation link")
        return redirect('register')

@login_required(login_url='accounts:login')
def dashboard(request):

    return render(request,'accounts/dashboard.html')

def forgotPassword(request):

    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)

            #FORGOT PASSWORD RESET MAIL
            current_site = get_current_site(request)
            mail_subject = 'Please Reset Your Account'
            message = render_to_string('accounts/password_reset_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),



            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,"Password reset mail has sent to the email address")
            return redirect('accounts:resetPassword')
        else:
            messages.error(request,'Account does not exist')
            return redirect('account:forgotPassword')

    return render(request,'accounts/forgotPassword_email.html')

def resetPassword_Validate(request,uidb64,token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request,'Please Reset Your Password')
        return redirect('accounts:resetPassword')
    else:
        messages.error(request,"Link Has been Expired")
        return redirect('accounts:login')
    

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirmPassword = request.POST['Confirmpassword']
        if password == confirmPassword:
            uid = request.session.get('uid')
            user = Account.objects.get(pk = uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset Succesfully')
            return redirect('accounts:login')
        else:
            messages.error('Password Does not Matching')
            return redirect('accounts/resetPassword.html')
    else:
        
        return render(request,'accounts/resetPassword.html')