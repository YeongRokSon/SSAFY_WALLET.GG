from rest_framework import serializers
from .models import Article, Comment
from accounts.models import User # 유저 닉네임 보여주기 위해

# 댓글 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # ID 대신 유저아이디(문자)
    nickname = serializers.ReadOnlyField(source='user.nickname') # 닉네임
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('user','article','nickname') # 작성자랑 글번호는 자동

# 게시글 시리얼라이저
class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # ID 대신 유저아이디(문자)
    nickname = serializers.ReadOnlyField(source='user.nickname') # 닉네임
    comments = CommentSerializer(many=True, read_only=True) # 댓글도 같이 보여주기
    
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('user',)