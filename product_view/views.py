from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer

class Product(APIView):
    def post(self,request):
        user=request.user
        if not user.is_authenticated:
            return Response({
                'success':False,
                'message':'Authentication Required'
            },status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_seller:
            return Response({
                'success': False,
                'message': 'Only seller can post'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer=ProductSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success':True,
                'message':'the product posted successfully'
            },status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'the product not posted successfully',
            'errors':serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
