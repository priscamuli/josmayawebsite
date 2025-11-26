from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, Category, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .mpesa import lipa_na_mpesa
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.forms import AuthenticationForm





# Create your views here.
def custom_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "store/login.html", {"form": form})

def home(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')

    products = Product.objects.all()
    categories = Category.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product_id)[:4]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products
    })



def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    # Category Filter
    category = request.GET.get('category')
    if category:
        products = products.filter(category__id=category)

    # Sorting
    sort = request.GET.get('sort')
    if sort == "low-high":
        products = products.order_by('price')
    elif sort == "high-low":
        products = products.order_by('-price')
    elif sort == "newest":
        products = products.order_by('-id')

    return render(request, 'store/shop.html', {
        'products': products,
        'categories': categories
    })


@login_required
def add_to_cart(request, product_id):
    quantity = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    request.session['cart'] = cart
    return redirect('cart')


@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        items.append({'product': product, 'quantity': qty})
        total += product.price * qty
    return render(request, 'store/cart.html', {'items': items, 'total': total})

# Remove from Cart
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart')


# Signup
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})

@csrf_exempt   # ONLY for Ngrok testing 
@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    # Calculate total amount
    total = 0
    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        total += product.price * qty

    if request.method == "POST":
        phone = request.POST.get('phone', '').strip()
        location = request.POST.get('location', '').strip()
        notify_phone = request.POST.get('notify_phone', '').strip()

        if not phone or not location or not notify_phone:
            messages.error(request, "All fields are required.")
            return redirect("checkout")


        # Format phone number for Daraja
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        elif phone.startswith("+"):
            phone = phone[1:]
        elif phone.startswith("7"):
            phone = "254" + phone

        # 💳 Send STK Push
        try:
            response = lipa_na_mpesa(phone, int(total))
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect("checkout")

        # 💾 Create Order with MerchantRequestID
        order = Order.objects.create(
            customer=request.user,
            total=total,
            status="Pending",
            mpesa_merchant_request_id=response.get("MerchantRequestID"), # Save ID for callback
            delivery_location=location,
            notify_phone=notify_phone
        )

        # 💾 Create OrderItems
        for pid, qty in cart.items():
            product = Product.objects.get(id=pid)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.price
            )

        # Clear cart
        request.session['cart'] = {}

        messages.success(request, "STK Push sent! Check your phone to complete payment.")
        return redirect("order_success")

    return render(request, 'store/checkout.html', {"total": total})

@login_required
def order_success(request):
    return render(request, 'store/order_success.html')

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).order_by('-ordered_at')
    return render(request, 'store/order_history.html', {'orders': orders})

def initiate_payment(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        response = lipa_na_mpesa(phone, int(amount))
        return render(request, 'store/payment_result.html', {'response': response})
    return render(request, 'store/pay.html')

import json
from django.http import JsonResponse
from .models import Order

@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    # Validate JSON
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception as e:
        return JsonResponse({"error": "Invalid JSON", "details": str(e)}, status=400)

    # Extract callback data
    stk_callback = data.get("Body", {}).get("stkCallback", {})
    merchant_request_id = stk_callback.get("MerchantRequestID")
    result_code = stk_callback.get("ResultCode")

    if not merchant_request_id:
        return JsonResponse({"error": "Missing MerchantRequestID"}, status=400)

    # Update order
    try:
        order = Order.objects.get(mpesa_merchant_request_id=merchant_request_id)
        order.status = "Paid" if result_code == 0 else "Failed"
        order.save()
    except Order.DoesNotExist:
        # Avoid breaking callback if order not found
        pass

    # Always respond with success to M-Pesa
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})




@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    items = order.items.all()  # Using related_name from OrderItem

    return render(request, 'store/order_detail.html', {
        'order': order,
        'items': items
    })
