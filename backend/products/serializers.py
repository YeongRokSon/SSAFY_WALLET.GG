from rest_framework import serializers
from .models import Product, ProductOption

class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = '__all__'
        read_only_fields = ('product',) # 상품에 종속된 거라 읽기 전용

class ProductSerializer(serializers.ModelSerializer):
    # [중요] models.py에서 related_name='options'로 설정했으므로
    # source='productoption_set'은 삭제해야 합니다.
    # 필드명(options)과 related_name(options)이 같으면 source를 안 써도 됩니다.
    options = ProductOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'