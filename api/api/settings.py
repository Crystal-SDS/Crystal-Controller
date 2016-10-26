"""
Django settings for controller project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import redis

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WORKLOAD_METRICS_DIR = os.path.join("/opt", "crystal", "workload_metrics")
NATIVE_FILTERS_DIR = os.path.join("/opt", "crystal", "native_filters")
STORLET_FILTERS_DIR = os.path.join("/opt", "crystal", "storlet_filters")
GLOBAL_NATIVE_FILTERS_DIR = os.path.join("/opt", "crystal", "global_native_filters")
DEPENDENCY_DIR = os.path.join("/opt", "crystal", "dependencies")
ANSIBLE_DIR = os.path.join(BASE_DIR, "swift", "ansible")
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&yx_=2@s(evyq=l9t2efrgmgryz^ea85$csdb_rprvc-9b&#r8' # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'rest_framework',
    'filters',
    'bw',
    'swift',
    'registry'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.middleware.CrystalMiddleware',
)

ROOT_URLCONF = 'api.urls'

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

WSGI_APPLICATION = 'api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# Simple sqlite3 database to avoid errors pop up during testing initialization
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'CET'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

# Keystone
KEYSTONE_ADMIN_URL = "http://localhost:5000/v2.0"
KEYSTONE_URL = "http://localhost:35357/v2.0"

# Swift
SWIFT_URL = "http://localhost:8080/"
SWIFT_API_VERSION = "v1"

# Redis
REDIS_CON_POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)

# SDS Project
STORLET_BIN_DIR = "/opt/ibm"
STORLET_DOCKER_IMAGE = "192.168.2.1:5001/ubuntu_14.04_jre8_storlets"
STORLET_TAR_FILE = "ubuntu_14.04_jre8_storlets.tar"

# Openstack Admin
MANAGEMENT_ACCOUNT = "management"
MANAGEMENT_ADMIN_USERNAME = "manager"
MANAGEMENT_ADMIN_PASSWORD = "manager"  # noqa

# pyactive
PYACTIVE_TRANSPORT = "tcp"
PYACTIVE_IP = "127.0.0.1"
PYACTIVE_PORT = 6899
PYACTIVE_URL = PYACTIVE_TRANSPORT+'://'+PYACTIVE_IP+':'+str(PYACTIVE_PORT)

# Metrics
METRIC_CLASS = 'registry.dynamic_policies.metrics.swift_metric'
METRIC_MAIN = 'SwiftMetric'

# Rules
RULE_CLASS = 'registry.dynamic_policies.rules.rule'
RULE_MAIN = 'Rule'
RULE_TRANSIENT_CLASS = 'registry.dynamic_policies.rules.rule_transient'
RULE_TRANSIENT_MAIN = 'TransientRule'
