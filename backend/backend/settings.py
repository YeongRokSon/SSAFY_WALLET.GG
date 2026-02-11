from pathlib import Path
from dotenv import load_dotenv
import os
import environ


# 1. 환경변수 초기화 (django-environ 활용)
env = environ.Env(
    # 타입 캐스팅 기본값 설정 (디버그 모드 등)
    DEBUG=(bool, False)
)

# BASE_DIR 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 읽기
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 2. 보안 설정
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*'] # 배포 시에는 구체적인 도메인으로 변경 필요


# 3. Application definition
INSTALLED_APPS = [
    # Django 기본 앱
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', # dj-rest-auth registration 사용 시 필수

    # Third Party Apps (명세서 기반 필수 라이브러리)
    'rest_framework',           # DRF
    'rest_framework.authtoken', # 토큰 인증
    'dj_rest_auth',             # 회원가입/인증
    'dj_rest_auth.registration', # 회원가입 기능 활성화
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',              # Vue와 통신을 위한 CORS

    # Local Apps (기능별 앱 분리 예시)
    'accounts',    # F02: 회원 커스터마이징 (User 모델)
    'articles',    # F07: 커뮤니티
    'products',
    'services',
    'youtube',
    'animals',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # CORS 미들웨어 (최상단 권장)
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # allauth 필수 미들웨어
]

ROOT_URLCONF = 'backend.urls' # 프로젝트명에 맞게 수정

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# 4. Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# 5. Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# 6. Internationalization (한국 설정)
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True


# 7. Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'


# 8. Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- [Project Custom Settings] ---

# 9. Custom User Model 설정 (필수 요구사항 F02)
AUTH_USER_MODEL = 'accounts.User'

# 10. DRF 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# 10-1. django-allauth 설정 (dj_rest_auth registration 사용 시 필수)
SITE_ID = 1

# 11. CORS 설정 (Vue 개발 서버 포트 허용)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 12. API Key 관리 (환경변수에서 로드)
# 금융감독원 API (예적금)
FINLIFE_API_KEY = env('FINLIFE_API_KEY')

# 카카오 맵 API (은행 검색, 경로 안내)
KAKAO_MAP_API_KEY = env('KAKAO_MAP_API_KEY')

# 유튜브 API (관심 종목)
YOUTUBE_API_KEY = env('YOUTUBE_API_KEY')

# AI 모델 설정 (GMS 활용)
# OpenAI 라이브러리가 자동으로 인식하는 변수명은 아닐 수 있으니,
# views.py에서 client 생성할 때 이 변수들을 가져다 쓰면 돼.
GMS_API_KEY = env('GMS_API_KEY')
GMS_BASE_URL = env('GMS_BASE_URL') # GMS 엔드포인트

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'