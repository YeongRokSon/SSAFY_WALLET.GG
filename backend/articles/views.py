from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Article, Comment
from .serializers import ArticleSerializer, CommentSerializer

# [기존] 게시글 목록 & 작성
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def article_list(request):
    if request.method == 'GET':
        articles = Article.objects.all().order_by('-pk')
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE']) # PUT과 DELETE를 추가해!
@permission_classes([IsAuthenticatedOrReadOnly])
def article_detail(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)

    # 1. 조회 (GET)
    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    # 2. 수정 (PUT)
    elif request.method == 'PUT':
        # 작성자 본인인지 확인하는 센스!
        if request.user != article.user:
            return Response({'error': '본인 글만 수정할 수 있어!'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    # 3. 삭제 (DELETE)
    elif request.method == 'DELETE':
        if request.user != article.user:
            return Response({'error': '본인 글만 삭제할 수 있어!'}, status=status.HTTP_403_FORBIDDEN)
        
        article.delete()
        return Response({'message': '글이 삭제됐어.'}, status=status.HTTP_204_NO_CONTENT)

# ★ [추가] 댓글 작성 (POST)
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # 로그인한 사람만
def comment_create(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(article=article, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ★ [추가] 댓글 수정 및 삭제 (하나의 주소에서 처리)
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated]) # 로그인한 사람만 가능
def comment_detail(request, comment_pk):
    # 1. 댓글이 있는지 확인하고 가져오기
    comment = get_object_or_404(Comment, pk=comment_pk)

    # 2. 본인 댓글인지 확인 (권한 체크)
    if request.user != comment.user:
        return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    # --- [수정 로직: PUT] ---
    if request.method == 'PUT':
        # partial=True를 쓰면 내용(content)만 보내도 에러 없이 잘 수정돼!
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    # --- [삭제 로직: DELETE] ---
    elif request.method == 'DELETE':
        comment.delete()
        return Response({'message': '삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)