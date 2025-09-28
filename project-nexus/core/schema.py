import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Order, OrderItem
from users.models import User

# User Types
class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "username", "first_name", "last_name")

# Product Types
class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

# Order Types
class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# Query Class
class Query(graphene.ObjectType):
    # User queries
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.Int(required=True))
    
    # Product queries
    products = graphene.List(ProductType)
    product_by_id = graphene.Field(ProductType, id=graphene.Int(required=True))
    products_by_category = graphene.List(ProductType, category_id=graphene.Int(required=True))
    search_products = graphene.List(ProductType, query=graphene.String(required=True))
    
    # Category queries
    categories = graphene.List(CategoryType)
    category_by_id = graphene.Field(CategoryType, id=graphene.Int(required=True))
    
    # Order queries
    my_orders = graphene.List(OrderType)
    order_by_id = graphene.Field(OrderType, id=graphene.Int(required=True))
    
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required!")
        return user
    
    def resolve_users(self, info):
        user = info.context.user
        if not user.is_staff:
            raise Exception("Staff permission required!")
        return get_user_model().objects.all()
    
    def resolve_user_by_id(self, info, id):
        user = info.context.user
        if not user.is_staff:
            raise Exception("Staff permission required!")
        return get_user_model().objects.get(id=id)
    
    def resolve_products(self, info):
        return Product.objects.filter(is_active=True).select_related('category')
    
    def resolve_product_by_id(self, info, id):
        return Product.objects.get(id=id, is_active=True)
    
    def resolve_products_by_category(self, info, category_id):
        return Product.objects.filter(category_id=category_id, is_active=True)
    
    def resolve_search_products(self, info, query):
        return Product.objects.filter(
            name__icontains=query,
            is_active=True
        )[:20]  # Limit results
    
    def resolve_categories(self, info):
        return Category.objects.all()
    
    def resolve_category_by_id(self, info, id):
        return Category.objects.get(id=id)
    
    def resolve_my_orders(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required!")
        return Order.objects.filter(user=user).prefetch_related('items')
    
    def resolve_order_by_id(self, info, id):
        user = info.context.user
        order = Order.objects.get(id=id)
        if not user.is_staff and order.user != user:
            raise Exception("Permission denied!")
        return order

# Mutations
class CreateUserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        username = graphene.String(required=True)
    
    user = graphene.Field(UserType)
    
    def mutate(self, info, email, password, username):
        User = get_user_model()
        user = User(email=email, username=username)
        user.set_password(password)
        user.save()
        return CreateUserMutation(user=user)

class CreateProductMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(required=True)
        category_id = graphene.Int(required=True)
    
    product = graphene.Field(ProductType)
    
    def mutate(self, info, name, description, price, stock, category_id):
        user = info.context.user
        if not user.is_staff:
            raise Exception("Staff permission required!")
        
        category = Category.objects.get(id=category_id)
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category
        )
        product.save()
        return CreateProductMutation(product=product)

class CreateOrderMutation(graphene.Mutation):
    class Arguments:
        product_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)
    
    order = graphene.Field(OrderType)
    
    def mutate(self, info, product_id, quantity):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required!")
        
        product = Product.objects.get(id=product_id, is_active=True)
        
        if product.stock < quantity:
            raise Exception("Insufficient stock!")
        
        # Create or get pending order
        order, created = Order.objects.get_or_create(
            user=user,
            status='pending',
            defaults={'total_amount': 0}
        )
        
        # Create order item
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )
        
        if not created:
            order_item.quantity += quantity
            order_item.save()
        
        # Update order total
        order.total_amount = sum(item.price * item.quantity for item in order.items.all())
        order.save()
        
        # Update product stock
        product.stock -= quantity
        product.save()
        
        return CreateOrderMutation(order=order)

class UpdateOrderStatusMutation(graphene.Mutation):
    class Arguments:
        order_id = graphene.Int(required=True)
        status = graphene.String(required=True)
    
    order = graphene.Field(OrderType)
    
    def mutate(self, info, order_id, status):
        user = info.context.user
        if not user.is_staff:
            raise Exception("Staff permission required!")
        
        order = Order.objects.get(id=order_id)
        order.status = status
        order.save()
        return UpdateOrderStatusMutation(order=order)

class Mutation(graphene.ObjectType):
    # Authentication
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    
    # User mutations
    create_user = CreateUserMutation.Field()
    
    # Product mutations
    create_product = CreateProductMutation.Field()
    
    # Order mutations
    create_order = CreateOrderMutation.Field()
    update_order_status = UpdateOrderStatusMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)