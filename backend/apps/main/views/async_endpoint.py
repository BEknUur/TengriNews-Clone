from django.conf import settings
from django.http import JsonResponse
from django.views import View  
from apps.main.utils.async_client import fetch_external, ExternalAPIError
from apps.main.utils.cache import make_article_detail_key, cache_get, cache_set 
import asyncio

class ExternalDataView(View):
    async def get(self, request, *args, **kwargs):
        q = request.GET.get("q", "").strip()
        if not q:
            return JsonResponse({"detail": "missing q parameter"}, status=400)

        cache_key = f"external:data:q:{q}"
        cached = None
        try:
            cached = cache_get(cache_key)
        except Exception:
            cached = None

        if cached is not None:
            return JsonResponse(cached, status=200, safe=False)

        url = settings.EXTERNAL_API_URL  
        params = {"q": q}

        try:
            data = await fetch_external(url, params=params, headers={"Accept": "application/json"})
        except ExternalAPIError as exc:
            if cached is not None:
                return JsonResponse(cached, status=200, safe=False)
            return JsonResponse({"detail": "external service error"}, status=502)

        processed = data  

        try:
            cache_set(cache_key, processed, settings.EXTERNAL_API_TTL)
        except Exception:
            pass

        return JsonResponse(processed, status=200, safe=False)