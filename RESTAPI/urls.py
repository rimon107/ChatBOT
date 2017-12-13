from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

urlpatterns = {

    url(r'^get_response$', GetResponseResult, name="query"),


}

urlpatterns = format_suffix_patterns(urlpatterns)