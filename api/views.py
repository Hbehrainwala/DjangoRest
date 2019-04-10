from django.shortcuts import render
from django.http import HttpResponse

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import User, Product, Order
from . import serializers


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return self.queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = serializers.UserCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            user = serializer.instance
            user.set_password(data.get('password'))
            user.customer = True
            user.save()
            return Response({
                'status': status.HTTP_201_CREATED,
                'message': 'Customer Signup Successfully.',
            })

        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Please provide required fields.',
            'error' : serializer.errors
        })


class UserLoginView(APIView):
    """
    It's user login view. accepted method post. it's return always new token. and endpoint is /api/login.
    """
    # permission_classes = (AllowAny,)
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        try:
            user.auth_token.delete()    
        except Exception as e:
            pass

        token, created = Token.objects.get_or_create(user=user)
        headers = {
            'access_token' : token.key,
            'Access-Control-Expose-Headers': 'access_token'
        }
        return Response({
            "status": status.HTTP_200_OK,
            "message" : 'Successfully login.',
            'user' : serializers.UserSerializer(user).data
        }, headers=headers)

class UserLogoutView(APIView):
    """
    IT's user logout view. accepted method post. endpoint is /api/logout.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        token = Token.objects.get(key=request.auth.key)
        token.delete()
        return Response({
            "status": status.HTTP_200_OK,
            "message": 'Successfully logout.'
        })

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = serializers.ProductCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': status.HTTP_201_CREATED,
                'message': 'Product Added Successfully.',
            })

        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Please provide required fields.',
            'error' : serializer.errors
        })

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users create and fetch orders.
    """
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.customer:
            return self.queryset.filter(customer=user)
        return self.queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = serializers.OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response({
                'status': status.HTTP_201_CREATED,
                'message': 'Order Placed Successfully.',
            })

        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Please provide required fields.',
            'error' : serializer.errors
        })

    @action(detail=True)
    def accept_order(self, request, pk=None):
        user = request.user
        if user.provider:
            order = Order.objects.filter(pk=int(pk)).first()
            if not order:
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'No order found.',
                })
            if order.check_for_accept:
                order.status = Order.STATE.ACCEPTED
                order.provider = user
                order.save()
                return Response({
                    'status' : status.HTTP_200_OK,
                    'message' : "Order Accepted Successfully"
                })

            return Response({
                'status' : status.HTTP_200_OK,
                'message' : "Order is Not Available for Accept"
            })

        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Only provider accept order.',
        })            