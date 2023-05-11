from django.shortcuts import render , redirect
from django.views import View
from . models import * 
from django.db.models import Count
from . forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
import datetime, random
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.
# @login_required
def home(request):
    return render(request,"app/home.html")

def about(request):
    return render(request,"app/about.html")

def contact(request):
    return render(request,"app/contact.html")

@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request , "app/category.html",locals())
@method_decorator(login_required,name='dispatch')

class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request , "app/category.html",locals())

@method_decorator(login_required,name='dispatch')

class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)

        return render(request , "app/productdetail.html",locals())
@method_decorator(login_required,name='dispatch')

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User Registered Successfully")
        else: 
            messages.warning(request,"Invalid Input Data")
        return render(request, 'app/customerregistration.html',locals())
@method_decorator(login_required,name='dispatch')

class ProfileView(View):
        def get(self,request):
            form = CustomerProfileForm()
            return render(request, 'app/profile.html',locals())


        def post(self,request):
            form = CustomerProfileForm(request.POST)
            if form.is_valid():
                user = request.user
                name = form.cleaned_data['name']
                locality = form.cleaned_data['locality']                
                city = form.cleaned_data['city']
                mobile = form.cleaned_data['mobile']
                state = form.cleaned_data['state']
                zipcode = form.cleaned_data['zipcode']

                reg = Customer(user=user, name=name, locality=locality, mobile=mobile, city=city, state=state, zipcode=zipcode)
                reg.save()
                messages.success(request, "Congratulations! Profile Save Successfull")
            else:
                messages.warning(request,"Invalid Input")



            return render(request, 'app/profile.html',locals())
@login_required
def address(request):
    add= Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',locals())

@method_decorator(login_required,name='dispatch')

class updateAddress(View):
    def get(self, request, pk):
        add= Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html',locals())
    def post(self, request, pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']                
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, 'Congratulations! Profile update Successful')
        else:
            messages.warning(request, 'Invalid Input Data')
        return redirect('address')

# def add_to_cart(request):
#     user = request.user
#     product_id = request.GET.get('prod_id')
#     product = Product.objects.get(id=product_id)
#     Cart(user=user,product=product).save()
#     return redirect('/cart')
@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check if a cart item already exists for the user and the product
    cart_item = Cart.objects.filter(user=user, product=product).first()
    if cart_item:
        # If the quantity of the cart item is 0, delete it
        if cart_item.quantity == 0:
            cart_item.delete()
        else:
            # Otherwise, update the quantity of the existing cart item
            cart_item.quantity += 1
            cart_item.save()
    else:
        # Otherwise, create a new cart item
        Cart.objects.create(user=user, product=product, quantity=1)

    return redirect('showcart')
@login_required
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity + p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    return render( request, 'app/addtocart.html',locals())

@method_decorator(login_required,name='dispatch')

class checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value 
        totalamount = famount + 40
        return render(request, 'app/checkout.html',locals())

@login_required
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id)&Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)



@login_required
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id)&Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

@login_required
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id)&Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

@login_required
def payment(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0

    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    customer = Customer.objects.get(user=user)
    phone = customer.mobile
    khalti_test_key = settings.KHALTI_TEST_LIVE_SECRET_KEY
    khalti_live_key = settings.KHALTI_LIVE_SECRET_KEY
    key = "Key " + khalti_test_key
    data = {
  "return_url": "http://127.0.0.1:8000/paymentverify",
  "website_url": "https://example.com/",
  "amount": totalamount*100,
  "purchase_order_id": "product_id",
  "purchase_order_name": user.username,
   "customer_info": {
      "name": user.username,
      "email": user.email,
      "phone" : phone
      
  },
  }
    # replace the key with your live secret key
    headers = {
        "Authorization": "Key " + khalti_test_key
            # "Authorization": settings.KHALTI_LIVE_SECRET_KEY 

    }
    response = requests.post("https://a.khalti.com/api/v2/epayment/initiate/", json=data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        pidx = data.get("pidx")
        pay = Khalti(pidx=pidx, user_id=user.id) #pidx to database
        pay.save()
        
        return HttpResponseRedirect(data.get("payment_url"))
    else:
        # Handle any errors that occurred during the payment initiation process
        # return HttpResponse(key)
        # return HttpResponse("Error occurred while verifying payment: ")

        return HttpResponse("Error occurred while initiating payment: {}".format(response.text))
@login_required  
def paymentVerification(request):
    
    user = request.user
    user_id = user.id 
   
    khalti1 = Khalti.objects.filter(user_id=user_id )
    latest_pidx = Khalti.objects.filter(user_id=user_id).order_by('-timestamp').first()
    pidx = latest_pidx.pidx
    data2={
        "pidx" : pidx
    }
    headers2 = {
        "Authorization": "Key 3f4159b5f85840fdab55ce0670f53e6d" 
            # "Authorization": "Key live_secret_key_292ff997b479476b9fa2fb39fa715244"  
    }
    response = requests.post("https://a.khalti.com/api/v2/epayment/lookup/", json=data2, headers=headers2)
    if response.status_code == 200:
        data = response.json()
        pidx = data.get('pidx')
        status = data.get('status')
        txn_id = data.get('transaction_id')
        amount =  data.get('total_amount')/100
        # khalti1 = Khalti.objects.get(user_id=user_id )
        khalti1 = Khalti.objects.filter(user_id=user_id, pidx=pidx).latest('timestamp')
        

        khalti1.paymentstatus = status
        khalti1.txnid = txn_id
        khalti1.paidamount = amount
        khalti1.save()
        
        # creating a order number 
        # Get current date and time
        now = datetime.datetime.now()

        # Generate a random 4-digit number
        rand_num = random.randint(1000, 9999)

        # Create the order number string
        order_num = "ORD-{}-{}-{}-{}".format(now.year, str(now.month).zfill(2), str(now.day).zfill(2), str(now.hour).zfill(2) + str(now.minute).zfill(2), rand_num)

        
        if status == 'Completed':
            
            customer = Customer.objects.get(user=user)
            cart_items = Cart.objects.filter(user=user)
            order_list = []
            # Create an order for each item in the cart
            for item in cart_items:
                order = Order.objects.create(
                    user=user,
                    order_number=order_num,
                    customer=customer,
                    product=item.product,
                    quantity=item.quantity,
                    status="Pending",
                    paymentstatus=status
                )
                order_list.append(order)

            # Clear the cart
            cart_items.delete()
            context = {
                'order_list': order_list,
                'paid_amount': amount,
                'transaction_id': txn_id,
                'status': status,
            }
            # return HttpResponse(order_list)

            return render(request, 'app/payment_success.html',context)
        else:
            return render(request, 'app/payment_failure.html', locals())
    else:
        # return HttpResponse("Error occurred while verifying payment: {}")
        return HttpResponse("Error occurred while verifying payment: {}".format(response.text))





