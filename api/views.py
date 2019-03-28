from django.shortcuts import render
from django.http import HttpResponse

from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer, UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserSerializer

    def get_queryset(self):
    	return self.queryset

    def create(self, request, *args, **kwargs):
    	data = request.data
    	serializer = UserCreateSerializer(data=data)
    	if serializer.is_valid():
    		serializer.save()
    		user = serializer.instance
    		user.set_password(data.get('password'))
    		user.save()
    		return Response({
	            'status': status.HTTP_201_CREATED,
	            'message': 'User Created Successfully.',
	        })

    	return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Please provide required fields.',
            'error' : serializer.errors
        })
