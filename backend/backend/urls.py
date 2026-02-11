from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. 금융 상품 관련 (products 앱으로 가!)
    path('api/products/', include('products.urls')),
    
    # 2. 게시판 관련 (articles 앱으로 가!)
    path('articles/', include('articles.urls')),
    
    # 3. 회원가입/로그인 (dj-rest-auth 라이브러리 사용)
    path('accounts/', include('dj_rest_auth.urls')),
    path('accounts/signup/', include('dj_rest_auth.registration.urls')),
    
    # 4. 내 프로필 조회/수정 (accounts 앱으로 가!)
    path('accounts/', include('accounts.urls')),

    # 5. 각종 서비스 조회
    path('services/', include('services.urls')),

    # 6. 유튜브 관련(일단 북마크 기능만 여기로)
    path('youtube/', include('youtube.urls')),

    # 7. 동물 성향 파악
    path('api/animals/', include('animals.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
