from django.urls import path
from . import views

#doc
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.homepage, name='homepage'),

    #Document upload
    path('upload_file', views.upload_file, name='upload_file'),

    #feedback
    path('feedback', views.feedback, name='feedback'),
    
]


#doc settings for static folder
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




