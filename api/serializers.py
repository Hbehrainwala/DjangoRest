from rest_framework import serializers

from .models import User, Product, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'customer', 'provider', 'courier')

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name','password', 'customer', 'provider', 'courier')

    def validate(self, attrs):
        if not User.objects.filter(email=attrs.get('email')).exists():
            return attrs
        raise serializers.ValidationError({"email": "This email is taken already."})


class UserLoginSerializer(serializers.Serializer):
    """
    It's authentication serializer. it's valid method check if not valid user raise exception or if authenticate 
    return user.
    """
    email = serializers.EmailField(label=("Email"))
    password = serializers.CharField(label=("Password"), style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                if not user.is_active:
                    msg = ('User account is disabled.')
                    raise serializers.ValidationError(msg, code='authorization')
                attrs['user'] = user
                return attrs   
            msg = ('Unable to log in with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')
        msg = ('Must include "email" and "password".')
        raise serializers.ValidationError(msg, code='authorization')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'unit_single_name', 'unit_multi_name')

class ProductCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    unit_single_name = serializers.CharField(required=True)
    unit_multi_name = serializers.CharField(required=True)
    price = serializers.DecimalField(required=True, max_digits=6, decimal_places=2)

    class Meta:
        model = Product
        fields = ('title', 'description', 'unit_single_name', 'unit_multi_name', 'price')

    def validate(self, attrs):
        if not Product.objects.filter(title=attrs.get('title')).exists():
            return attrs
        raise serializers.ValidationError({"title": "This title is taken already."})


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')        

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ('customer', 'provider', 'courier', 'status', 'payment_status', 'payment_types', 'order_items')

    def create(self, validated_data, *args, **kwargs):
        item_datas = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item_data in item_datas:
            OrderItem.objects.create(order=order, **item_data)
        return order