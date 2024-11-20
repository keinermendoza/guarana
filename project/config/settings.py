import os
from pathlib import Path
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static

from dotenv import load_dotenv
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = bool(int(os.environ.get('DEBUG', '0')))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(' ')
CSRF_TRUSTED_ORIGINS =  os.environ.get('CSRF_TRUSTED_ORIGINS').split(' ')

INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_cotton',
    'django_htmx',
    'django_user_agents',
    'django_vite',

    'core',
    'api',
    # 'django_filters',
    'django_extensions',
    # 'rest_framework',

]
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    "django_htmx.middleware.HtmxMiddleware", # htmx
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware', # user_agent

]

COTTON_DIRS = [
    BASE_DIR / 'cotton_components',
    BASE_DIR / 'core/templates',
    BASE_DIR / 'blog/templates',
] 

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        ],
        # 'APP_DIRS': False,
        'OPTIONS': {
            "loaders": [
                # only change is to limit the available dirs 
                ("core.custom_cotton_loader.Loader", COTTON_DIRS), 
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "builtins": [
                "django_cotton.templatetags.cotton",
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            
        },
    },
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(levelname)s - %(asctime)s - %(name)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": [],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}


WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en'

LANGUAGES = [
('en', _('English')),
('es', _('Spanish')),
('pt', _('Portuguese'))
]

TIME_ZONE = 'America/Manaus'

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
BASE_DIR / 'locale',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ]
}



# Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('ENGINE', 'django.db.backends.sqlite3'),
        'HOST': os.environ.get('SQL_HOST'),
        'USER': os.environ.get('USER'),
        'NAME': os.environ.get('NAME',  BASE_DIR / 'db.sqlite3'),
        'PASSWORD': os.environ.get('PASSWORD'),
        'PORT': os.environ.get('SQL_PORT'),
    }
}

# Statics
    
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media/'

STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles'
]

DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG
    }
}

# Email
# EMAIL_HOST = os.environ.get('EMAIL_HOST')
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))
# EMAIL_USE_TLS = bool(os.environ.get('EMAIL_USE_TLS'))

# # Url
ROOT_URLCONF = os.environ.get('ROOT_URLCONF', 'config.urls')


UNFOLD = {
    "STYLES": [
        lambda request: static("css/tailwind.css"),
    ],
    "SCRIPTS": [
        lambda request: static("admin/js/prevent_duplicate_submition.js")
    ],
    "SITE_HEADER": _("Loja de Guaraná Admin"),
    "SITE_TITLE": _("Loja de Guaraná"),
    "SITE_SYMBOL": "settings",
    # "SHOW_HISTORY": True,
    # "DASHBOARD_CALLBACK": "core.admin.get_extra_context",
    "SIDEBAR": {
        "show_search": False,  # Search in applications and models names
        "show_all_applications": False,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("Inicio"),
                "items": [
                    {
                        "title": "Ver Graficos",
                        "icon": "home",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        "permission": lambda request: request.user.is_superuser,
                    },],
            },
            {
                "title": _("Registrar"),
                "separator": True,  # Top border
                "items": [
                    {
                        "title": "Nova Venda",
                        "icon": "trending_up",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_venta_add"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": "Nova Produção",
                        "icon": "factory",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_produccion_add"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                "title": _("Modelos"),
                "separator": True,  # Top border
                "collapsible": True,  # Collapsible group of links
                "items": [
                    {
                        "title": "Periodo",
                        "icon": "calendar_month",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_periodo_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": "Tipos de Guaraná",
                        "icon": "splitscreen_left",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_tipoguarana_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": "Formas de Pagamento",
                        "icon": "add_card",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_metodopago_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": "Sacos",
                        "icon": "inventory_2",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_saco_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": "Produtos",
                        "icon": "shopping_cart",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_producto_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                   
                ],
            },
             {
                "title": _("Operações"),
                "separator": True,  # Top border
                "collapsible": True,  # Collapsible group of links
                "items": [
                     {
                        "title": "Vendas",
                        "icon": "trending_up",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_venta_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": "Produções",
                        "icon": "factory",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_produccion_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": "Pagamentos Recebidos",
                        "icon": "request_quote",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_usometodopago_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },

                    {
                        "title": "Compra de Vidros",
                        "icon": "local_mall",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:core_compravidros_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
        ],
    },
}