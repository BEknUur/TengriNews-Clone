from types import SimpleNamespace

from django.test import RequestFactory
from django.http import HttpResponse

import pytest

from apps.core.locale_middleware import CustomLocaleMiddleware


def get_response(request):
    return HttpResponse()


def make_middleware():
    return CustomLocaleMiddleware(get_response)


def test_user_preferred_language():
    rf = RequestFactory()
    request = rf.get("/")
    request.user = SimpleNamespace(is_authenticated=True, preferred_language="kk")

    mw = make_middleware()
    response = mw(request)

    assert request.LANGUAGE_CODE == "kk"
    assert response.headers.get("Content-Language") == "kk"


def test_app_language_header_over_accept_and_default():
    rf = RequestFactory()
    request = rf.get("/", HTTP_APP_LANGUAGE="ru")
    request.user = SimpleNamespace(is_authenticated=False)

    mw = make_middleware()
    response = mw(request)

    assert request.LANGUAGE_CODE == "ru"
    assert response.headers.get("Content-Language") == "ru"


def test_query_param_lang_and_normalization():
    rf = RequestFactory()
    request = rf.get("/?lang=en_US")
    request.user = SimpleNamespace(is_authenticated=False)

    mw = make_middleware()
    response = mw(request)

    assert request.LANGUAGE_CODE == "en"
    assert response.headers.get("Content-Language") == "en"


def test_accept_language_fallback_and_default():
    rf = RequestFactory()
    # include unsupported first, supported second
    request = rf.get("/", HTTP_ACCEPT_LANGUAGE="de, ru;q=0.8")
    request.user = SimpleNamespace(is_authenticated=False)

    mw = make_middleware()
    response = mw(request)

    assert request.LANGUAGE_CODE == "ru"
    assert response.headers.get("Content-Language") == "ru"


def test_unsupported_languages_fall_back_to_default():
    rf = RequestFactory()
    request = rf.get("/", HTTP_ACCEPT_LANGUAGE="de, fr;q=0.8")
    request.user = SimpleNamespace(is_authenticated=False)

    mw = make_middleware()
    response = mw(request)

    assert request.LANGUAGE_CODE == mw.DEFAULT_LANGUAGE
    assert response.headers.get("Content-Language") == mw.DEFAULT_LANGUAGE
