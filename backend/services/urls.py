from django.urls import path
from . import views

urlpatterns = [
    path('gold-silver/', views.get_market_indices), # 금/은/코인/환율 시세
    path('bank-search/', views.search_bank),       # 은행 지도 검색
    path('route/', views.route_guide),             # 길찾기
    path('ai-consult/', views.ai_financial_consult), # AI 상담
]