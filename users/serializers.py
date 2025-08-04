from rest_framework import serializers
from .models import Seller
class SellerSerializer(serializers.ModelSerializer):
    seller_rating= serializers.SerializerMethodField()
    class Meta:
        model=Seller
        fields=['seller_user','seller_store_name','seller_rating']

    def get_seller_rating(self,obj):
        from django.db.models import Avg
        result = obj.products.aggregate(average_rating=Avg('p_rating'))
        avg=result['average_rating']
        if avg is None:
            return 0.0
        return avg