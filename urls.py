from django.conf.urls import *
import forms_builder.forms.urls # add this import

from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('crowdataapp', )
}

urlpatterns = patterns('',
                       url(r'', include('django_browserid.urls')),
                       url(r'^cd/', include('crowdataapp.urls')),
                       url(r'^$', include('crowdataapp.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^forms/', include(forms_builder.forms.urls)),
                       (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)
