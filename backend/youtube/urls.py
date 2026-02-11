from django.urls import path
from . import views

urlpatterns = [
    # 영상 검색: /youtube/search/?q=검색어
    path('search/', views.youtube_search),
    
    # 북마크 토글 (저장/삭제): /api/youtube/bookmark/ (POST)
    path('bookmark/', views.toggle_bookmark),
    
    # 내 북마크 목록 조회: /api/youtube/bookmark/list/ (GET)
    path('bookmark/list/', views.get_bookmarked_videos),
    # [추가] 영상 상세 정보 조회 (이 부분이 없어서 404 오류 발생)
    path('video/', views.video_detail),
]