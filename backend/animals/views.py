from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .data import QUESTIONS, ANIMALS

# [추가] 분석 기록 저장을 위해 다른 앱(products)의 모델을 가져옵니다.
from products.models import UserPortfolio 

# 1. 질문지 전송 API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_survey_questions(request):
    data = []
    for q in QUESTIONS:
        options = [{"text": opt["text"]} for opt in q["options"]]
        data.append({
            "id": q["id"],
            "question": q["question"],
            "options": options
        })
    return Response(data)

# 2. 결과 계산 및 저장 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_survey_result(request):
    user_answers = request.data.get('answers')
    user_info = request.data.get('user_info') # [중요] 프론트에서 보낸 자산+목표 정보 받기

    if not user_answers or len(user_answers) != 10:
        return Response({'error': '모든 문항에 답해주세요.'}, status=400)

    # 1. 점수 계산
    scores = {animal: 0 for animal in ANIMALS.keys()}
    for idx, answer_index in enumerate(user_answers):
        try:
            selected_option = QUESTIONS[idx]['options'][int(answer_index)]
            for animal, score in selected_option['scores'].items():
                scores[animal] += score
        except (IndexError, ValueError):
            continue

    best_animal = max(scores, key=scores.get)
    animal_info = ANIMALS[best_animal]
    
    # 분석 결과 데이터 구성 (응답 및 저장용)
    analysis_result = {
        "animal": best_animal,
        "name": animal_info['name'],
        "description": animal_info['description'],
        "stats": animal_info.get('stats', {}),
    }

    # 2. User 모델 업데이트 (기본 정보 동기화)
    user = request.user
    user.investment_persona = best_animal
    
    # [추가] 자산 정보가 같이 왔다면 User 테이블의 필드도 업데이트
    if user_info:
        # assets -> money 필드 매핑 주의
        user.age = int(user_info.get('age', user.age) or 0)
        user.money = int(user_info.get('assets', user.money) or 0) 
        user.salary = int(user_info.get('salary', user.salary) or 0)
    
    user.save() # 여기서 1차 저장 (User 테이블)

    # 3. [추가] 포트폴리오 기록 저장 (UserPortfolio 테이블)
    # 여기에 goal, tendency 등 User 모델에 없는 정보까지 모두 JSON으로 저장됨
    if user_info:
        UserPortfolio.objects.create(
            user=user,
            user_info=user_info,        # { age, salary, assets, goal, tendency } -> 통째로 저장
            analysis_result=analysis_result # { animal, name, description, stats } -> 통째로 저장
        )

    # 4. 결과 반환
    return Response(analysis_result)