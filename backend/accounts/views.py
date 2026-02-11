from rest_framework.decorators import api_view, permission_classes, parser_classes # ★ parser_classes 추가
from rest_framework.parsers import MultiPartParser, FormParser # ★ 박스 뜯는 도구 가져오기
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .utils import make_nick

User = get_user_model()

# 회원가입 (기존과 동일)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    data = request.data.copy()
    if not data.get('nickname'):
        data['nickname'] = make_nick()

    serializer = UserSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({'message': '가입 성공!'}, status=status.HTTP_201_CREATED)

# 프로필 조회, 수정, 탈퇴 (수정됨!)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
# ★ 사진과 글자가 섞인 'FormData'를 읽을 수 있게 도구를 챙겨줘!
@parser_classes([MultiPartParser, FormParser]) 
def profile(request, username):
    user = get_object_or_404(User, username=username)

    # 1. 정보 조회 (GET)
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # 2. 정보 수정 (PUT)
    elif request.method == 'PUT':
        if request.user.username != username:
            return Response({'error': '본인만 수정할 수 있어!'}, status=status.HTTP_403_FORBIDDEN)
            
        # ★ partial=True가 있어야 빈 칸이 있어도 에러가 안 나!
        serializer = UserSerializer(user, data=request.data, partial=True) 
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    # 3. 회원 탈퇴 (DELETE)
    elif request.method == 'DELETE':
        if request.user.username != username:
            return Response({'error': '본인만 탈퇴할 수 있어!'}, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response({'message': '탈퇴 완료'}, status=status.HTTP_204_NO_CONTENT)