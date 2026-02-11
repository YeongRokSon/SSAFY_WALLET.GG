from django.db.models import Max, Count, Min, Q
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests
import json 
from openai import OpenAI
import yfinance as yf
import traceback
from .models import Product, ProductOption, UserPortfolio
from .serializers import ProductSerializer, ProductOptionSerializer
# ------------------------------------------------------
# [New Helper] ETF/주식 데이터 수집 및 저장
# ------------------------------------------------------
def fetch_and_save_etfs():
    # 추천할 종목 리스트 (직접 큐레이션)
    symbols = [
        {'symbol': 'SPY', 'name': 'SPDR S&P 500', 'desc': '미국 S&P500 지수 추종 ETF (안정적 우상향)'},
        {'symbol': 'QQQ', 'name': 'Invesco QQQ', 'desc': '나스닥 100 추종 (기술주 중심 성장)'},
        {'symbol': 'SCHD', 'name': 'Schwab US Dividend', 'desc': '미국 배당 성장 ETF (현금 흐름 중시)'},
        {'symbol': 'TQQQ', 'name': 'ProShares UltraPro QQQ', 'desc': '나스닥 3배 레버리지 (고위험 고수익)'},
        {'symbol': 'O', 'name': 'Realty Income', 'desc': '매달 월세를 받는 리츠(부동산) 주식'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc', 'desc': '전기차 및 AI 선두 기업'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corp', 'desc': 'AI 반도체 대장주'},
        {'symbol': 'GLD', 'name': 'SPDR Gold Shares', 'desc': '금 현물 투자 ETF (안전자산)'},
        {'symbol': 'AAPL', 'name': 'Apple Inc', 'desc': '아이폰, 맥북 등을 만드는 세계 1위 기술 기업'},
        {'symbol': 'MSFT', 'name': 'Microsoft', 'desc': '윈도우, 오피스, 클라우드(Azure) 및 AI 선두 기업'},
        {'symbol': 'GOOGL', 'name': 'Alphabet (Google)', 'desc': '검색 엔진, 유튜브, 안드로이드 운영체제 보유'},
        {'symbol': 'AMZN', 'name': 'Amazon', 'desc': '세계 최대 이커머스 및 클라우드(AWS) 기업'},
        {'symbol': 'TSLA', 'name': 'Tesla', 'desc': '전기차 시장의 선두주자 및 자율주행 기술 보유'},
        {'symbol': 'NVDA', 'name': 'NVIDIA', 'desc': 'AI 컴퓨팅의 핵심인 GPU 반도체 시장 지배자'},
        {'symbol': 'META', 'name': 'Meta Platforms', 'desc': '페이스북, 인스타그램, 왓츠앱 등 소셜 미디어 제국'},
        {'symbol': 'NFLX', 'name': 'Netflix', 'desc': '글로벌 1위 OTT 스트리밍 서비스'},
        {'symbol': 'SBUX', 'name': 'Starbucks', 'desc': '세계 최대의 커피 프랜차이즈'},
        {'symbol': 'KO', 'name': 'Coca-Cola', 'desc': '워렌 버핏이 사랑하는 필수 소비재 배당주'},
        {'symbol': 'O', 'name': 'Realty Income', 'desc': '매달 배당을 주는 미국의 대표적인 리츠(부동산) 주식'},
    ]

    saved_count = 0
    
    for item in symbols:
        try:
            ticker = yf.Ticker(item['symbol'])
            # fast_info가 더 빠르고 안정적일 수 있음
            info = ticker.info 
            
            # 가격 및 수익률 정보 추출
            current_price = info.get('currentPrice') or info.get('regularMarketPreviousClose', 0)
            
            # 1년 수익률 (52WeekChange 활용, 0.15 -> 15.0)
            return_1y = info.get('52WeekChange', 0) * 100
            dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0

            # 1. Product 저장
            product, created = Product.objects.update_or_create(
                fin_prdt_cd=item['symbol'], # 티커를 고유 코드로 사용
                defaults={
                    'kor_co_nm': '미국 주식/ETF',
                    'fin_prdt_nm': item['name'],
                    'etc_note': item['desc'],
                    'product_type': 'etf', # 타입 지정
                    'join_deny': 1,
                }
            )

            # 2. ProductOption 저장 (옵션은 하나만 생성)
            ProductOption.objects.update_or_create(
                product=product,
                defaults={
                    'fin_prdt_cd': item['symbol'],
                    'intr_rate_type_nm': '투자 수익률',
                    'intr_rate': round(return_1y, 2),       # 1년 수익률
                    'intr_rate2': round(dividend_yield, 2), # 배당률
                    'save_trm': 12, # 기준 12개월
                    'etc_info': {
                        'current_price': current_price,
                        'sector': info.get('sector', 'ETF'),
                        'currency': info.get('currency', 'USD'),
                    }
                }
            )
            saved_count += 1
            
        except Exception as e:
            print(f"ETF 저장 실패 ({item['symbol']}): {e}")
            continue

    return saved_count
# ------------------------------------------------------------------
# 1. 금융감독원 데이터 가져오기 & 저장하기 (핵심 로직)
# ------------------------------------------------------------------
# ------------------------------------------------------
# 1. [Helper 함수] 6개 금융 API 데이터 통합 호출 및 저장
# ------------------------------------------------------
def fetch_and_save_products():
    api_key = settings.FINLIFE_API_KEY
    # [중요] 기존 데이터 초기화
    Product.objects.all().delete()

    # 6개 API URL 정의
    API_URLS = {
        'deposit': 'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json',       
        'saving': 'http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json',         
        'annuity': 'http://finlife.fss.or.kr/finlifeapi/annuitySavingProductsSearch.json', 
        'mortgage': 'http://finlife.fss.or.kr/finlifeapi/mortgageLoanProductsSearch.json', 
        'rent': 'http://finlife.fss.or.kr/finlifeapi/rentHouseLoanProductsSearch.json',    
        'credit': 'http://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json',     
    }

    results = {} 
    total_saved = 0
    
    # API 순회
    for product_type, url in API_URLS.items():
        # 연금저축은 보험 권역(050000), 나머지는 은행(020000)
        fin_grp_no = '050000' if product_type == 'annuity' else '020000'
        
        params = {
            'auth': api_key,
            'topFinGrpNo': fin_grp_no, 
            'pageNo': 1,
            'numOfRows': 100 
        }
        
        try:
            response = requests.get(url, params=params)
            response_json = response.json()
            
            if 'result' not in response_json:
                results[product_type] = "Error: result 키 없음"
                continue 

            base_list = response_json['result'].get('baseList', [])
            option_list = response_json['result'].get('optionList', [])
            
            saved_count = 0

            # (1) 상품 기본 정보 저장
            for item in base_list:
                fin_prdt_cd = item.get('fin_prdt_cd')
                
                if Product.objects.filter(fin_prdt_cd=fin_prdt_cd).exists():
                    continue

                def safe_int(value):
                    if value is None or value == "": return 0
                    try: return int(value)
                    except: return 0

                save_data = {
                    'fin_prdt_cd': fin_prdt_cd,
                    'kor_co_nm': item.get('kor_co_nm'),
                    'fin_prdt_nm': item.get('fin_prdt_nm'),
                    'etc_note': item.get('etc_note', ''),
                    'join_deny': safe_int(item.get('join_deny')), 
                    'join_member': item.get('join_member', ''),
                    'join_way': item.get('join_way', ''),
                    'spcl_cnd': item.get('spcl_cnd', ''),
                    'product_type': product_type, 
                }
                
                if product_type in ['deposit', 'saving']:
                     save_data['mtrt_int'] = item.get('mtrt_int', '')

                serializer = ProductSerializer(data=save_data)
                if serializer.is_valid():
                    serializer.save()
                    saved_count += 1
                    total_saved += 1

            # (2) 상품 옵션 저장
            for item in option_list:
                fin_prdt_cd = item.get('fin_prdt_cd')
                product = Product.objects.filter(fin_prdt_cd=fin_prdt_cd).first()

                if not product:
                    continue 

                def safe_float(value):
                    if value is None or value == "": return -1.0
                    try: return float(value)
                    except: return -1.0

                def safe_int_opt(value):
                    if value is None or value == "": return 0
                    try: return int(value)
                    except: return 0

                rate_1 = -1.0
                rate_2 = -1.0
                rate_type_nm = ''
                save_trm = None 
                etc_info = {}   

                # A. 예금 / 적금
                if product_type in ['deposit', 'saving']:
                    rate_1 = safe_float(item.get('intr_rate'))
                    rate_2 = safe_float(item.get('intr_rate2'))
                    rate_type_nm = item.get('intr_rate_type_nm', '')
                    save_trm = safe_int_opt(item.get('save_trm'))

                # B. 대출 (주택/전세)
                elif product_type in ['mortgage', 'rent']:
                    rate_1 = safe_float(item.get('lend_rate_min')) 
                    rate_2 = safe_float(item.get('lend_rate_max')) 
                    rate_type_nm = item.get('lend_rate_type_nm', '') 
                    etc_info = {
                        'rpay_type_nm': item.get('rpay_type_nm'), 
                        'mrtg_type_nm': item.get('mrtg_type_nm'), 
                    }

                # C. 신용대출
                elif product_type == 'credit':
                    grades = [
                        item.get('crdt_grad_1'), item.get('crdt_grad_4'), item.get('crdt_grad_5'),
                        item.get('crdt_grad_6'), item.get('crdt_grad_10'), item.get('crdt_grad_11'),
                        item.get('crdt_grad_12'), item.get('crdt_grad_13')
                    ]
                    valid_rates = [float(g) for g in grades if g is not None and g != '']
                    if valid_rates:
                        rate_1 = min(valid_rates)
                        rate_2 = max(valid_rates)
                    
                    rate_type_nm = item.get('crdt_prdt_type_nm', '신용대출')
                    etc_info = {'crdt_prdt_type_nm': item.get('crdt_prdt_type_nm')}

                # D. 연금저축
                elif product_type == 'annuity':
                    rate_1 = safe_float(item.get('pnsn_recp_amt')) # 수령액
                    rate_2 = 0 
                    
                    rate_type_nm = item.get('pnsn_recp_trm_nm', '연금') 
                    paym_prd = safe_int_opt(item.get('paym_prd'))
                    save_trm = paym_prd * 12 if paym_prd else None 
                    
                    etc_info = {
                        'pnsn_entr_age_nm': item.get('pnsn_entr_age_nm'),
                        'pnsn_strt_age_nm': item.get('pnsn_strt_age_nm'),
                        'mon_paym_atm_nm': item.get('mon_paym_atm_nm'),
                        'paym_prd_nm': item.get('paym_prd_nm'),
                    }

                if ProductOption.objects.filter(
                    product=product, 
                    save_trm=save_trm, 
                    intr_rate_type_nm=rate_type_nm
                ).exists():
                    continue

                save_data = {
                    'fin_prdt_cd': fin_prdt_cd,
                    'intr_rate_type_nm': rate_type_nm,
                    'intr_rate': rate_1,   
                    'intr_rate2': rate_2, 
                    'save_trm': save_trm,
                    'etc_info': etc_info
                }
                
                serializer = ProductOptionSerializer(data=save_data)
                if serializer.is_valid():
                    serializer.save(product=product)
            
            results[product_type] = f"{saved_count}개 저장 성공"

        except Exception as e:
            print(f"Error saving {product_type}: {e}")
            results[product_type] = f"Error: {str(e)}"
            continue

    return {"status": True, "message": f"총 {total_saved}개 신규 상품 저장 완료", "details": results}


# ------------------------------------------------------
# 2. 기본 View 함수 (조회, 저장)
# ------------------------------------------------------

# [F03-1] 데이터 저장
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def save_deposit_products(request):
    result = fetch_and_save_products()
    # 2. ETF 상품 추가 수집
    etf_count = fetch_and_save_etfs()
    
    result['message'] += f" + ETF {etf_count}개 저장"
    return Response(result)

# DB 저장 현황 체크
@api_view(['GET'])
@permission_classes([AllowAny])
def check_db_status(request):
    counts = Product.objects.values('product_type').annotate(count=Count('id'))
    return Response({
        'total_products': Product.objects.count(),
        'by_type': counts
    })

# [F03-2] 상품 목록 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    if not Product.objects.exists():
        fetch_and_save_products()

    sort = request.query_params.get('sort')
    product_type = request.query_params.get('type')
    bank = request.query_params.get('bank')
    term = request.query_params.get('term')
    
    # [수정] UnboundLocalError 방지: 변수 초기화
    products = Product.objects.all()
    
    if product_type:
        if product_type == 'loan':
             products = products.filter(product_type__in=['mortgage', 'rent', 'credit'])
        else:
            products = products.filter(product_type=product_type)

    if bank and bank != 'null':
        products = products.filter(kor_co_nm=bank)

    if term and term != 'null':
        try:
            # [수정] productoption -> options (related_name 반영)
            products = products.filter(options__save_trm=int(term)).distinct()
        except ValueError:
            pass

    # [수정] productoption -> options (related_name 반영)
    products = products.annotate(
        max_rate=Max('options__intr_rate2'), 
        min_rate=Min('options__intr_rate'),
        max_amt=Max('options__intr_rate') 
    )

    is_loan_type = product_type in ['mortgage', 'rent', 'credit', 'loan']
    is_annuity = product_type == 'annuity'
    is_investment = product_type in ['etf']

    if sort == 'top_rate':
        if is_loan_type:
            products = products.order_by('min_rate') 
        elif is_annuity:
            products = products.order_by('-max_amt') 
        elif is_investment:
            # [수정] ETF/주식은 수익률(intr_rate=max_amt) 기준으로 정렬
            products = products.order_by('-max_amt') 
        else:
            products = products.order_by('-max_rate') 
    elif sort == 'dividend':
        # [신규] 배당률(intr_rate2=max_rate) 높은순
        products = products.order_by('-max_rate')        
    elif sort == 'popular':
        products = products.annotate(join_count=Count('join_users')).order_by('-join_count')
        
    else:
        if is_loan_type: products = products.order_by('min_rate')
        elif is_annuity: products = products.order_by('-max_amt')
        elif is_investment: products = products.order_by('-max_amt') # 기본도 수익률순
        else: products = products.order_by('-max_rate')

    # 연금/대출은 기본금리(intr_rate), 예적금은 우대금리(intr_rate2) 기준!
    if product_type in ['annuity', 'mortgage', 'rent', 'credit', 'loan']:
        products = Product.objects.annotate(max_rate=Max('options__intr_rate'))
    else:
        products = Product.objects.annotate(max_rate=Max('options__intr_rate2'))

    if product_type:
        if product_type == 'loan': # 대출은 3종류 한꺼번에!
            products = products.filter(product_type__in=['mortgage', 'rent', 'credit'])
        else:
            products = products.filter(product_type=product_type)

    if bank:
        products = products.filter(kor_co_nm=bank)

    if term and product_type not in ['mortgage', 'rent', 'credit', 'loan']:
        products = products.filter(options__save_trm=term)

    # 정렬: 대출은 낮은 금리순, 나머지는 높은 금리순!
    if sort == 'top_rate':
        if product_type in ['mortgage', 'rent', 'credit', 'loan']:
            products = products.order_by('max_rate')
        else:
            products = products.order_by('-max_rate')
    
    serializer = ProductSerializer(products.distinct(), many=True)
    return Response(serializer.data)


# [F03-3] 상품 상세 조회 및 가입
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def product_detail(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    serializer = ProductSerializer(product)
    
    data = serializer.data
    
    # 로그인 상태라면 좋아요/가입 여부를 확인해서 같이 보냄
    if request.user.is_authenticated:
        data['is_liked'] = product.like_users.filter(pk=request.user.pk).exists()
        data['is_joined'] = product.join_users.filter(pk=request.user.pk).exists()
    else:
        data['is_liked'] = False
        data['is_joined'] = False
        
    return Response(data)

# [F09] 기본 추천 알고리즘
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_product(request):
    user = request.user
    similar_users = user.__class__.objects.filter(
        age__range=(user.age - 5, user.age + 5),
        money__range=(user.money - 10000000, user.money + 10000000)
    ).exclude(pk=user.pk)

    recommended = {}
    for similar_user in similar_users:
        for product in similar_user.joined_products.all():
            if product in recommended:
                recommended[product] += 1
            else:
                recommended[product] = 1

    sorted_products = sorted(recommended.items(), key=lambda x: x[1], reverse=True)[:5]
    result_products = [item[0] for item in sorted_products] 

    serializer = ProductSerializer(result_products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_portfolio(request):
    try:
        portfolio = UserPortfolio.objects.filter(user=request.user).latest('created_at')
        return Response({'exists': True, 'analysis_result': portfolio.analysis_result})
    except:
        return Response({'exists': False})


# ------------------------------------------------------------------
# 4. AI 분석 & 추천 기능
# ------------------------------------------------------------------

# [4-1] 투자 성향 분석
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_analyze_user(request):
    client = OpenAI(
        api_key=settings.GMS_API_KEY,      
        base_url=settings.GMS_BASE_URL
    )
    user_info = request.data.get('user_info')
    
    system_instruction = "너는 금융 전문가야. 답변은 반드시 순수한 JSON 형식으로만 해줘."
    user_prompt = f"[사용자 정보] {json.dumps(user_info, ensure_ascii=False)} 분석 결과 JSON: {{ 'type': '성향', 'score': 점수, 'advice': '조언' }}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 모델 이름 꼭 확인!
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"}
        )
        
        # ★ AI가 보낸 텍스트에서 JSON만 깨끗하게 뽑아내기
        raw_content = response.choices[0].message.content
        result = json.loads(raw_content) 

        # DB에 저장 (migrate가 되어있어야 해!)
        UserPortfolio.objects.create(
            user=request.user, 
            user_info=user_info, 
            analysis_result=result
        )
        return Response(result)
        
    except Exception as e:
        print(f"❌ 분석 중 에러 발생: {e}") # 터미널 창을 확인해봐!
        return Response({'error': 'AI 분석 실패'}, status=500)
    
# [4-2] 내 분석 기록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_portfolio(request):
    try:
        portfolio = UserPortfolio.objects.filter(user=request.user).latest('created_at')
        return Response({
            'exists': True, 
            'user_info': portfolio.user_info,
            'analysis_result': portfolio.analysis_result,
            'date': portfolio.created_at
        })
    except UserPortfolio.DoesNotExist:
        return Response({'exists': False})

# [4-3] AI 상품 추천 (수치와 데이터를 사용한 구체화 버전)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_recommend_product(request):
    client = OpenAI(
        api_key=settings.GMS_API_KEY,      
        base_url=settings.GMS_BASE_URL
    )
    analysis_result = request.data.get('analysis_result')
    
    # 1. 추천 후보 상품들 가져오기 (금리 높은 순 20개)
    products = Product.objects.annotate(max_rate=Max('options__intr_rate2')).order_by('-max_rate')[:100]
    
    # 2. [수정] 리스트 컴프리헨션 대신 일반 for문으로 텍스트 생성
    candidates_list = []
    for p in products:
        item_text = f"- 상품명: {p.fin_prdt_nm}, 금융사: {p.kor_co_nm}, 최고금리: {p.max_rate}%, 유형: {p.product_type}, 특징: {p.etc_note[:50]}"
        candidates_list.append(item_text)
    
    candidates_text = "\n".join(candidates_list)

    # 3. [강화] AI에게 내리는 전문적인 지시사항 (Persona)
    system_instruction = """
    너는 대한민국 최고의 자산관리사(CFA)이자 금융 분석 전문가야. 
    사용자의 분석 결과와 제공된 금융 상품 데이터를 정밀하게 대조해서 가장 수익률이 높고 적합한 6개를 추천해줘.
    
    반드시 지켜야 할 규칙:
    1. 추천 이유(reason)에 반드시 구체적인 '수치'를 포함할 것 (예: 금리 %, 수익률 %, 자산 대비 비율 등).
    2. 타 상품이나 시장 평균 대비 어떤 장점이 있는지 비교 데이터를 언급할 것.
    3. 사용자의 투자 성향(분석 결과)과 상품의 위험도를 논리적으로 연결할 것.
    4. 사용자의 상황을 간단히 브리핑 해줄것
    5. 답변은 반드시 순수한 JSON 형식으로만 할 것.
    """

    user_prompt = f"""
    [사용자 투자 성향 분석 결과]
    {json.dumps(analysis_result, ensure_ascii=False)}

    [추천 후보 상품 리스트]
    {candidates_text}

    위 데이터를 기반으로 다음 JSON 형식에 맞춰 5개를 추천해줘:
    {{
      "recommendations": [
        {{
          "name": "정확한 상품명",
          "reason": "데이터와 수치를 기반으로 한 아주 구체적인 추천 이유 (최소 2문장 이상)"
        }}
      ]
    }}
    """

    try:
        # 모델은 gpt-4o 등 성능 좋은 모델로 설정해서 쓰면 돼!
        response = client.chat.completions.create(
            model="gpt-5.2", # 성능 좋은 모델 사용
            messages=[
                {"role": "system", "content": system_instruction}, 
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        ai_data = json.loads(response.choices[0].message.content)
        
        final_result = []
        for item in ai_data.get('recommendations', []):
            product = Product.objects.filter(fin_prdt_nm__contains=item['name']).first()
            if product:
                # 좋아요 여부 확인
                is_liked = product.like_users.filter(pk=request.user.pk).exists()
                
                final_result.append({
                    "id": product.pk,
                    "fin_prdt_cd": product.fin_prdt_cd, # 찜하기를 위해 코드 추가
                    "name": product.fin_prdt_nm,
                    "bank": product.kor_co_nm,
                    "reason": item.get('reason'),
                    "is_liked": is_liked
                })
        
        return Response(final_result)

    except Exception as e:
        print("🚨 AI 추천 로직에서 에러 발생!!!")
        traceback.print_exc() 
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------------------------------------------------------------
# 5. 찜하기(Like) / 가입하기 기능
# ------------------------------------------------------------------

# [5-1] 찜하기(Like) 토글
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_product(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    
    if product.like_users.filter(pk=request.user.pk).exists():
        product.like_users.remove(request.user)
        return Response({'is_liked': False, 'message': '관심 상품에서 해제되었습니다.'})
    else:
        product.like_users.add(request.user)
        return Response({'is_liked': True, 'message': '관심 상품에 등록되었습니다.'})
# [5-2] 가입하기 (Join) - 실제 가입 내역
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_product(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    
    if product.join_users.filter(pk=request.user.pk).exists():
        product.join_users.remove(request.user)
        return Response({'is_joined': False, 'message': '가입 내역이 삭제되었습니다.'})
    else:
        product.join_users.add(request.user)
        return Response({'is_joined': True, 'message': '가입 상품으로 등록되었습니다.'})

# 내 목록 조회 (프로필 페이지용)

# [5-1-1] 찜하기 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_liked_products(request):
    liked_products = request.user.liked_products.all()
    serializer = ProductSerializer(liked_products, many=True)
    return Response(serializer.data)

# [5-2-1] 내가 가입한 상품 목록
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_joined_products(request):
    joined_products = request.user.joined_products.all()
    serializer = ProductSerializer(joined_products, many=True)
    return Response(serializer.data)


