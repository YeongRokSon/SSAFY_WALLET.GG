from django.db import models
from django.conf import settings

# 1. [통합된] 상품 기본 정보
class Product(models.Model):
    # 상품 유형 구분
    PRODUCT_TYPE_CHOICES = [
        ('deposit', '정기예금'),
        ('saving', '적금'),
        ('annuity', '연금저축'),
        ('mortgage', '주택담보대출'),
        ('rent', '전세자금대출'),
        ('credit', '개인신용대출'),
        ('etf', 'ETF/주식'),
    ]

    fin_prdt_cd = models.TextField(unique=True) # 상품 코드
    kor_co_nm = models.TextField()              # 금융회사명
    fin_prdt_nm = models.TextField()            # 상품명
    
    # 빈 값(blank) 허용
    etc_note = models.TextField(null=True, blank=True)      # 기타 유의사항
    join_deny = models.IntegerField(null=True, blank=True)  # 가입 제한
    join_member = models.TextField(null=True, blank=True)   # 가입 대상
    join_way = models.TextField(null=True, blank=True)      # 가입 방법
    spcl_cnd = models.TextField(null=True, blank=True)      # 우대 조건
    
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='deposit')

    mtrt_int = models.TextField(null=True, blank=True)    
    max_limit = models.BigIntegerField(null=True, blank=True) 
    
    # 가입한 유저
    join_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='joined_products', 
        blank=True
    )

    # ★ [이동됨] 관심 등록한 유저 (좋아요 기능) - Product 모델 안에 있어야 합니다!
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='liked_products', 
        blank=True
    )

    def __str__(self):
        return f"[{self.get_product_type_display()}] {self.fin_prdt_nm}"


# 2. [통합된] 상품 옵션
class ProductOption(models.Model):
    # related_name='options' 필수
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    fin_prdt_cd = models.TextField()           
    
    # 금리 유형명도 비어있을 수 있으므로 허용
    intr_rate_type_nm = models.CharField(max_length=100, default='', blank=True) 
    
    intr_rate = models.FloatField(default=-1)  
    intr_rate2 = models.FloatField(default=-1) 
    
    save_trm = models.IntegerField(null=True, blank=True) 

    etc_info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.intr_rate_type_nm}"


# 3. [신규] AI 분석 기록 (UserPortfolio)
class UserPortfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_info = models.JSONField()
    analysis_result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}의 분석 기록"