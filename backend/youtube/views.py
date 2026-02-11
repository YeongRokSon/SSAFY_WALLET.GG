from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from accounts.models import SavedVideo
import requests

# 1. 유튜브 영상 검색 (로그인 없이 가능) - [F05] 유튜브 영상 검색 (API 중계)
@api_view(['GET'])
@permission_classes([AllowAny])
def youtube_search(request):
    query = request.query_params.get('q')
    
    if not query:
        return Response({'message': '검색어를 입력해주세요.'}, status=400)

    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        return Response({'message': '서버에 YouTube API 키가 설정되지 않았습니다.'}, status=500)

    url = 'https://www.googleapis.com/youtube/v3/search'
    
    params = {
        'key': api_key,
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': 12,
        'regionCode': 'KR',
        'order': 'relevance' # 관련도 순
    }

    try:
        res = requests.get(url, params=params)
    
        # 유튜브 API 쿼터 초과 등의 에러 처리
        if res.status_code != 200:
            return Response(res.json(), status=res.status_code)
        return Response(res.json())
    except Exception as e:
        return Response({'error': str(e)}, status=500)
# [신규] 영상 상세 정보 조회 (조회수, 설명 등)
@api_view(['GET'])
@permission_classes([AllowAny])
def video_detail(request):
    video_id = request.GET.get('id')
    if not video_id:
        return Response({'error': 'ID required'}, status=400)
        
    api_key = settings.YOUTUBE_API_KEY
    # part에 'statistics'를 포함해야 조회수 확인 가능
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet,statistics"
    
    try:
        res = requests.get(url)
        return Response(res.json())
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
# 2. 북마크 추가/해제 (로그인 필수)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_bookmark(request):
    user = request.user
    video_id = request.data.get('videoId')
    
    if not video_id:
        return Response({'error': '영상 ID가 필요합니다.'}, status=400)

    # 이미 북마크 되어있는지 확인
    if SavedVideo.objects.filter(user=user, video_id=video_id).exists():
        # 있으면 삭제 (북마크 해제)
        SavedVideo.objects.filter(user=user, video_id=video_id).delete()
        return Response({'bookmarked': False, 'message': '북마크가 해제되었습니다.'})
    
    else:
        # 없으면 저장 (북마크 추가)
        SavedVideo.objects.create(
            user=user,
            video_id=video_id,
            title=request.data.get('title'),
            thumbnail=request.data.get('thumbnail'),
            channel_title=request.data.get('channelTitle'),
            published_at=request.data.get('publishTime')
        )
        return Response({'bookmarked': True, 'message': '북마크에 저장되었습니다.'})


# 3. 내 북마크 목록 조회 (로그인 필수)
# 프론트엔드에서 유튜브 API 결과와 동일한 구조로 데이터를 쓰기 위해 변환해서 반환
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookmarked_videos(request):
    bookmarks = SavedVideo.objects.filter(user=request.user).order_by('-created_at')
    
    # YouTube API 응답 구조(items 배열)와 비슷하게 포맷팅
    data = []
    for b in bookmarks:
        data.append({
            'id': { 'videoId': b.video_id },
            'snippet': {
                'title': b.title,
                'thumbnails': { 'high': { 'url': b.thumbnail } },
                'channelTitle': b.channel_title,
                'publishTime': b.published_at,
                'description': '' # 저장된 설명이 없으면 빈 문자열
            }
        })
        
    return Response(data)