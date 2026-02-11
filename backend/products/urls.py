from django.urls import path
from . import views

urlpatterns = [

    # 1. 데이터 관리
    path('save-deposit-products/', views.save_deposit_products),
    path('check-status/', views.check_db_status),

    # 2. 상품 조회
    path('', views.product_list),
    path('<int:product_pk>/', views.product_detail),

    # 3. 찜하기(Like) & 가입하기(Join) 기능
    path('<int:product_pk>/like/', views.like_product), # 찜하기 (장바구니)
    path('<int:product_pk>/join/', views.join_product), # 가입하기 (포트폴리오)
    
    # 4. 내 목록 조회 (프로필 페이지용)
    path('liked-list/', views.get_liked_products),   # 찜한 목록
    path('joined-list/', views.get_joined_products), # 가입한 목록

    # 5. AI 및 포트폴리오
    path('analyze/', views.ai_analyze_user),
    path('portfolio/latest/', views.get_latest_portfolio),
    path('ai-recommend/', views.ai_recommend_product),
    path('recommend/', views.recommend_product),

]