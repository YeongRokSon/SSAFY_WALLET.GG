# backend/services/views.py
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import yfinance as yf

# ------------------------------------------------------
# 1. [F04] 금/은 시세 데이터 (엑셀 파일 읽기)
# ------------------------------------------------------
import requests
import os
import pandas as pd

# [통합] 시장 지수 데이터 가져오기
@api_view(['GET'])
@permission_classes([AllowAny])
def get_market_indices(request):
    response_data = {
        'gold': [], 'silver': [], 'crypto': [], 'forex': []
    }

    # 1. Crypto & Forex (yfinance 사용 - 차트 데이터 확보용)
    symbols = [
        {'type': 'crypto', 'symbol': 'BTC-KRW', 'name': '비트코인', 'code': 'BTC'},
        {'type': 'crypto', 'symbol': 'ETH-KRW', 'name': '이더리움', 'code': 'ETH'},
        {'type': 'forex', 'symbol': 'KRW=X', 'name': '미국 달러', 'code': 'USD/KRW'},
        {'type': 'forex', 'symbol': 'JPYKRW=X', 'name': '일본 엔 (100)', 'code': 'JPY/KRW'},
    ]

    for item in symbols:
        try:
            # 최근 1달 데이터 가져오기
            ticker = yf.Ticker(item['symbol'])
            hist = ticker.history(period="1mo")
            
            if hist.empty: continue

            # 현재가 및 등락률 계산
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change_rate = ((current_price - prev_price) / prev_price) * 100

            # 차트용 히스토리 데이터 가공
            history_data = []
            for date, row in hist.iterrows():
                price = row['Close']
                # 엔화는 100엔 기준으로 변환
                if item['symbol'] == 'JPYKRW=X': price *= 100
                
                history_data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Close/Last': price
                })

            if item['symbol'] == 'JPYKRW=X': current_price *= 100

            asset_data = {
                'code': item['code'],
                'name': item['name'],
                'price': current_price,
                'change': round(change_rate, 2),
                'history': history_data
            }

            if item['type'] == 'crypto':
                response_data['crypto'].append(asset_data)
            else:
                response_data['forex'].append(asset_data)

        except Exception as e:
            print(f"Error fetching {item['symbol']}: {e}")

    # 2. Gold & Silver (로컬 엑셀 파일 사용 - 요청하신 방식)
    try:
        gold_file = os.path.join(settings.BASE_DIR, 'data', 'Gold_prices.xlsx')
        silver_file = os.path.join(settings.BASE_DIR, 'data', 'Silver_prices.xlsx')

        if os.path.exists(gold_file) and os.path.exists(silver_file):
            df_gold = pd.read_excel(gold_file)
            df_silver = pd.read_excel(silver_file)

            def clean_data(df):
                df.columns = df.columns.str.strip()
                price_col = None
                for col in ['Close/Last', 'Price', 'Close', 'USD (PM)']:
                    if col in df.columns:
                        price_col = col
                        break
                
                if not price_col: return []

                # 날짜 및 숫자 전처리
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values(by='Date')

                if df[price_col].dtype == 'object':
                    df[price_col] = df[price_col].astype(str).str.replace(',', '').str.replace('$', '')
                
                df[price_col] = pd.to_numeric(df[price_col])

                result = []
                for _, row in df.iterrows():
                    result.append({
                        'Date': row['Date'].strftime('%Y-%m-%d'),
                        'Close/Last': row[price_col]
                    })
                return result

            # 최근 50개 데이터만 반환
            response_data['gold'] = clean_data(df_gold)[-50:]
            response_data['silver'] = clean_data(df_silver)[-50:]
            
    except Exception as e:
        print(f"Error reading Excel files: {e}")

    return Response(response_data)
# ------------------------------------------------------
# 3. [F06] 카카오 은행 검색 & 경로 안내
# ------------------------------------------------------
@api_view(['GET'])
def search_bank(request):
    keyword = request.GET.get('keyword', '은행')
    # 기본값: 역삼 멀티캠퍼스
    x = request.GET.get('x', '127.039585') 
    y = request.GET.get('y', '37.5012743')
    
    api_key = settings.KAKAO_MAP_API_KEY
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
    headers = {'Authorization': f'KakaoAK {api_key}'}
    params = {'query': keyword, 'x': x, 'y': y, 'radius': 2000, 'sort': 'distance'}

    # ---------------------------------------------------------
    # [디버깅] 터미널로그 확인용
    print("=========================================")
    print(f"1. settings에서 가져온 키: [{api_key}]")
    print(f"2. 완성된 헤더: {headers}")
    print("=========================================")
    # ---------------------------------------------------------

    try:
        res = requests.get(url, headers=headers, params=params)
        # 만약 에러가 났다면 카카오가 보낸 진짜 에러 메시지를 봐야 함
        if res.status_code != 200:
            print(f"3. 카카오 응답 에러: {res.status_code} / {res.text}")
            
        return Response(res.json())
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def route_guide(request):
    # 출발지(sp), 도착지(ep) 좌표
    sp = request.GET.get('sp', '127.039585,37.5012743')
    ep = request.GET.get('ep')

    if not ep:
        return Response({'error': '목적지 좌표가 필요해!'}, status=400)

    api_key = settings.KAKAO_MAP_API_KEY
    url = 'https://apis-navi.kakaomobility.com/v1/directions'
    headers = {'Authorization': f'KakaoAK {api_key}', 'Content-Type': 'application/json'}
    params = {'origin': sp, 'destination': ep, 'priority': 'RECOMMEND'}

    try:
        res = requests.get(url, headers=headers, params=params)
        
        # 🔥 [디버깅 추가] 터미널에서 이 로그를 확인하세요!
        print("================ 카카오 응답 확인 ================")
        print(f"상태 코드: {res.status_code}")
        print(f"응답 본문: {res.json()}") 
        print("================================================")

        return Response(res.json())
     
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# ------------------------------------------------------
# 4. [심화] AI 금융 상담 (GMS / OpenAI)
# ------------------------------------------------------
@api_view(['POST'])
def ai_financial_consult(request):
    user_query = request.data.get('query')
    
    if not user_query:
        return Response({'error': '질문 내용을 입력해줘!'}, status=400)

    # GMS 엔드포인트 사용
    client = OpenAI(
        api_key=settings.GMS_API_KEY,
        base_url=settings.GMS_BASE_URL
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini", # 혹은 gpt-3.5-turbo 등 GMS 지원 모델
            messages=[
                {"role": "system", "content": "너는 친절한 금융 전문가야. 한국어로 명확하게 답변해줘."},
                {"role": "user", "content": user_query}
            ]
        )
        answer = completion.choices[0].message.content
        return Response({'answer': answer})
    except Exception as e:
        return Response({'error': str(e)}, status=500)