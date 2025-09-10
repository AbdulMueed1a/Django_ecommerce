from rest_framework import serializers
from .models import *
from order.models import OrderItems
from users.models import Seller

class ProductImageSerializer(serializers.ModelSerializer):
    image_url=serializers.SerializerMethodField()
    class Meta:
        model=ProductImage
        fields=['image_id']

    def get_image_url(self,obj):
        request=self.context.get('request')
        return request.build_absolute_uri(obj.image_pic.url) if obj.image_pic else None

class ProductSerializer(serializers.ModelSerializer):
    # user=serializers.HiddenField(default=serializers.CurrentUserDefault())
    # p_seller=serializers.HiddenField(default=Seller.objects.get(user=user.))

    class Meta:
        model = Product
        fields = [
            'p_id',
            'p_title',
            'p_description',
            'p_price',
            'p_category',
            'p_rating',
            'p_stock',
            'p_sold',
            'p_posted',
            'p_updated'
        ]
        read_only_fields = ['p_id', 'p_posted', 'p_updated', 'p_seller']

    def validate_p_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("The stock can't be less than zero")
        return value
    def validate_p_rating(self,value):
        if value<0:
            raise serializers.ValidationError("Product Rating can't be less then zero")
        elif value>5:
            raise serializers.ValidationError("Product Rating can't be more then 5")
        return value
    def validate_p_price(self,value):
        if value<0:
            raise serializers.ValidationError("Product price can't be negative")
        elif value==0:
            raise serializers.ValidationError("No free Products Allowed")
        return value
    def validate_p_sold(self,value):
        if value<0:
            raise serializers.ValidationError("Products sold can't be negative")
        return value

    def create(self, validated_data):
        user=self.context['request'].user
        seller=Seller.objects.get(user=user.id)
        return Product.objects.create(p_seller=seller,**validated_data)


class ProductReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductReviews
        fields='__all__'

    def validate_review_rating(self, value):
        if value < 0:
            raise serializers.ValidationError("Product Rating can't be less then zero")
        elif value > 5:
            raise serializers.ValidationError("Product Rating can't be more then 5")
        return value

    def validate(self,attrs):
        request=self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication required')
        user=request.user
        review_product=attrs.get('review_product')
        if not self.instance:
            if not review_product:
                review_product=self.instance.review_product
        else:
            if not review_product:
                raise serializers.ValidationError('No product object for review')

        if not OrderItems.objects.filter(
                order__order_user=user,
                order__order_status='completed',
                order_product=review_product,
                    ).exists():
            raise serializers.ValidationError('One must buy the product to give review')

class ReviewImageSerializer(serializers.ModelSerializer):
    image_url=serializers.SerializerMethodField()
    class Meta:
        model=ReviewImage
        fields=['review_image_id']

    def get_image_url(self,obj):
        request=self.context.get('request')
        return request.build_absolute_uri(obj.image_pic.url) if obj.image_pic else None

class ProductQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductQuestion
        fields=['question','answer','user']

    # def validator(self,obj):
    #     user=self.context.get('request').user
    #     if obj.user=user:

class ProductAnswerSerializer(serializers.ModelSerializer):
    seller_store = serializers.CharField(source='seller.seller_store_name', read_only=True)
    class Meta:
        model = ProductAnswers
        fields = ['question', 'answer', 'seller_store']
        read_only_fields=['seller']

    def validate(self, attr):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication required')
        question=attr['question']
        try:
            seller=request.user.seller
        except Seller.DoesNotExist:
            raise serializers.ValidationError('User is not the seller')
        if question.product.p_seller != seller:
            raise serializers.ValidationError('Only product seller can answer to this question')

class ProductCategoriesSerializer(serializers.ModelSerializer):
    parent=serializers.SerializerMethodField()
    breadcrumbs=serializers.SerializerMethodField()
    def get_parent(self,obj):
        if self.parent is not None:
            return ProductCategoriesSerializer(obj.parent.all(),many=True).data
        return []

    def get_breadcrumbs(self,obj):
        return[{"name":cat.name,'slug':cat.slug} for cat in obj.get_breadcrumbs()]