from uuid import uuid4
from django.shortcuts import redirect, render
import requests
from rest_framework.response import Response
from rest_framework import generics,permissions,viewsets
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpRequest
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import *
from .serializer import *
from .pagination import CustomPagination
from rest_framework import status
from django.contrib.auth import logout

# Create your views here.

class VendorList(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    


class VendorDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorDetailSerializer

    

class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = super().get_queryset()
        category_id = self.request.GET.get('category')
        if category_id:
            category = ProductCategory.objects.get(id=category_id)
            qs = qs.filter(category=category)
        
        if 'fetch_limit' in self.request.GET:
            limit = self.request.GET['fetch_limit']
            qs = qs[:int(limit)]
        return qs
    



class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer




class TagProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = super().get_queryset()
        tag = self.kwargs['tag']
        qs = qs.filter(tags__icontains=tag)
        return qs
    

@csrf_exempt
def CustomerLogin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username,password=password)
    if user:
        customer = Customer.objects.get(user=user)
        msg = {
        'bool': True,
        'user': user.username,
        'id': customer.id
        }
    else:
        msg = {
            'bool':False,
            'msg':'Invalid username or password !!'
        }
    return JsonResponse(msg)




@csrf_exempt
def CustomerRegister(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    username = request.POST.get('username')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    password = request.POST.get('password')
    hashed_password = make_password(password)
    try:
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_password
        )
               
        if user:
            try:
                #Create customer
                customer = Customer.objects.create(
                    user=user,
                    phone=phone,
                )
                msg = {
                'bool': True,
                'user': user.id,
                'customer': customer.id,
                'msg':'Thanks for your registration. Now you can login.'
                }
            except IntegrityError:
                msg = {
                'bool':False,
                'msg':"Phone already exist !!"
            }
        
        else:
            msg = {
                'bool':False,
                'msg':'Oops... Somethings went Wrong !!'
            }
    except IntegrityError:
        msg = {
            'bool':False,
            'msg':"Username already exist !!"
        }
    return JsonResponse(msg)



# @csrf_exempt
# def CustomerRegister(request):
#     if request.method == 'POST':
#         try:
#             first_name = request.POST.get('first_name')
#             last_name = request.POST.get('last_name')
#             username = request.POST.get('username')
#             email = request.POST.get('email')
#             phone = request.POST.get('phone')
#             password = request.POST.get('password')
#             hashed_password = make_password(password)

#             user = User.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 username=username,
#                 email=email,
#                 password=hashed_password
#             )

#             if user:
#                 customer = Customer.objects.create(
#                     user=user,
#                     phone=phone,
#                 )
#                 msg = {
#                     'bool': True,
#                     'user': user.id,
#                     'customer': customer.id,
#                     'msg': 'Thanks for your registration. Now you can login.'
#                 }
#         except IntegrityError as e:
#             if 'username' in str(e):
#                 msg = {
#                     'bool': False,
#                     'msg': "Username already exists!"
#                 }
#             elif 'phone' in str(e):
#                 msg = {
#                     'bool': False,
#                     'msg': "Phone number already exists!"
#                 }
#         else:
#             msg = {
#                 'bool': False,
#                 'msg': 'Oops... Something went wrong!'
#             }
#     else:
#         msg = {
#             'bool': False,
#             'msg': 'Invalid request method!'
#         }

#     return JsonResponse(msg)




class RelatedProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.kwargs['pk']
        product = Product.objects.get(id=product_id)
        qs = qs.filter(category=product.category).exclude(id=product_id)
        return qs


# class RelatedProductList(generics.ListAPIView):
#     serializer_class = ProductListSerializer

#     def get_queryset(self):
#         product_id = self.kwargs['pk']
#         product = Product.objects.get(id=product_id)
#         related_products = Product.objects.filter(category=product.category).exclude(id=product_id)
#         return related_products

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         data = serializer.data
#         for product in data:
#             product_id = product['id']
#             product['product_image'] = [image.image.url for image in Product.objects.get(id=product_id).product_image.all()]
#         return Response(data)

# class RelatedProductList(generics.ListAPIView):
#     serializer_class = ProductListSerializer

#     def get_queryset(self):
#         product_id = self.kwargs['pk']
#         product = Product.objects.get(id=product_id)
#         related_products = Product.objects.filter(category=product.category).exclude(id=product_id)
#         return related_products

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         data = serializer.data
#         for product in data:
#             product_id = product['id']
#             # Check if product_image exists and is not empty
#             if 'product_image' in product and product['product_image']:
#                 product['product_image'] = [image.image.url for image in Product.objects.get(id=product_id).product_image.all()]
#             else:
#                 # Set a default value for product_image
#                 product['product_image'] = []  # Or set it to a placeholder image URL
#         return Response(data)




class CustomerList(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    


class CustomerDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class UserDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer




class OrderList(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def post(self,request,*args, **kwargs):
        print(request.POST)
        return super().post(request,*args, **kwargs)
    

#### Order Items

class OrderItemsList(generics.ListCreateAPIView):
    queryset = OrderItems.objects.all()
    serializer_class = OrderItemSerializer

    


class OrderDetails(generics.ListAPIView):
    # queryset = Order.objects.all()
    serializer_class = OrderItemSerializer  

    def get_queryset(self):
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id)
        order_items = OrderItems.objects.filter(order=order)
        return order_items



class OerderItemList(generics.ListCreateAPIView):
    queryset = OrderItems.objects.all()
    serializer_class = OrderItemSerializer



class CustomerOrderItemsList(generics.ListAPIView):
    queryset = OrderItems.objects.all()
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id = self.kwargs['pk']
        qs = qs.filter(order__customer__id=customer_id)
        return qs



class OrderItemDetailS(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItems.objects.all()
    serializer_class = OrderItemSerializer



class CustomerAddressViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAddressSerializer
    queryset = CustomerAddress.objects.all()



class ProductRatingViewSet(viewsets.ModelViewSet):
    serializer_class = ProiductReviewSerializer
    queryset = ProductRating.objects.all()





################### product Category ###################

class CategoryList(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategoryDetailSerializer




@csrf_exempt
def Update_Order_Status(request, pk):
    order_id = pk
    if request.method == "POST":
        update_order_status = Order.objects.filter(id=order_id).update(order_status=True)
        msg = {
            'bool': False,
        }
        if update_order_status:
            msg = {
                'bool': True,
            }
        return JsonResponse(msg)
    


@csrf_exempt
def Update_Product_Download_Count(request, product_id):
    if request.method == "POST":
        product = Product.objects.get(id=product_id)
        totalDownloads = product.downloads
        totalDownloads += 1
        if totalDownloads == 0:
            totalDownloads = 1
        update_product_download_Count = Product.objects.filter(id=product_id).update(downloads=totalDownloads)
        msg = {
            'bool': False,
        }
        if update_product_download_Count:
            msg = {
                'bool': True,
            }
        return JsonResponse(msg)
    



### WishList
class Wish_List(generics.ListCreateAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer



@csrf_exempt
def check_in_wishlist(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        product_id = request.POST.get('product')
        if WishList.objects.filter(customer_id=customer_id, product_id=product_id).exists():
            return JsonResponse({'bool': True})
        else:
            return JsonResponse({'bool': False})
    return JsonResponse({'error': 'Invalid request method'}, status=405)



class Wish_Items(generics.ListAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id = self.kwargs['pk']
        qs = qs.filter(customer_id=customer_id)
        return qs



@csrf_exempt
def remove_from_wishlist(request):
    if request.method == 'POST':
        wishlist_id = request.POST.get('wishlist_id')
        response = WishList.objects.filter(id=wishlist_id).delete()
        msg = {'bool': False}
        if response[0]:
            msg = {'bool': True}
    return JsonResponse(msg)




from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
# Payment using Sslcommerz

base_url = 'http://127.0.0.1:8000'


@api_view(['POST'])
def initiate_payment(request):
    if request.method == 'POST':
        post_data = request.data
        print(post_data)
        order_id = post_data.get('order_id')
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order does not exist"}, status=400)
        
        total_amount = post_data.get('amount')
        
        customer = order.customer
        user = customer.user
        
        customer_address = customer.customer_address.filter(default_address=True).first()
        
        if not customer_address:
            return Response({"error": "Default customer address does not exist"}, status=400)
        print('Customer address founts',customer_address)
        transaction_id = uuid4().hex
        transaction = Transaction.objects.create(
            transaction_id=transaction_id,
            amount=total_amount,
            user=user,
            customer_address=customer_address,
            customer_email=user.email,
            customer_phone=customer.phone,
            customer_postcode=customer_address.post,
        )

        payment_data = {
            'store_id': 'kopot665596f0af929',
            'store_passwd': 'kopot665596f0af929@ssl',
            'total_amount': transaction.amount,
            'currency': transaction.currency,
            'tran_id': transaction.transaction_id,
            'product_name': 'Order Items',
            'product_category': 'Various',
            'product_profile': 'General',
            'success_url': f'{base_url}/api/success/',
            'fail_url': f'{base_url}/api/fail/',
            'cancel_url': f'{base_url}/api/cancel/',
            'shipping_method': 'Courier',
            'cus_country': 'Bangladesh',
            'cus_name': user.get_full_name(),
            'cus_email': transaction.customer_email,
            'cus_phone': transaction.customer_phone,
            'cus_add1': customer_address.address,
            'cus_city': 'Dhaka',
            'cus_postcode': transaction.customer_postcode,
            'ship_name': user.get_full_name(),
            'ship_add1': 'Dhaka',
            'ship_add2': 'Dhaka',
            'ship_city': 'Dhaka',
            'ship_state': 'Dhaka',
            'ship_postcode': 1000,
            'ship_country': 'Bangladesh',
            # Add any other required fields by SSLCommerz
        }
        print(payment_data)
        response = requests.post('https://sandbox.sslcommerz.com/gwprocess/v4/api.php', data=payment_data)
        return Response(response.json())


@api_view(['POST'])
def payment_success(request):
    if request.method == 'POST':
        post_data = request.POST
        transaction_id = post_data.get('tran_id')
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.status = 'SUCCESS'
            transaction.save()
            client_site_url = f'http://localhost:5173/payment_status?transaction_id={transaction_id}&status={transaction.status}'
            return redirect(client_site_url)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def payment_fail(request):
    if request.method == 'POST':
        post_data = request.POST
        transaction_id = post_data.get('tran_id')
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.status = 'FAILED'
            transaction.save()
            client_site_url = f'http://localhost:5173/paymentFail?transaction_id={transaction_id}&status={transaction.status}'
            return redirect(client_site_url)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def payment_cancel(request):
    if request.method == 'POST':
        post_data = request.POST
        transaction_id = post_data.get('tran_id')
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.status = 'CANCELLED'
            transaction.save()
            return Response({'status': 'cancelled'})
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

# Logout
@api_view(['POST'])
def logout_view(request):
    # # For token-based authentication
    # if request.auth:
    #     request.auth.delete()
    # For session-based authentication
    logout(request)
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
