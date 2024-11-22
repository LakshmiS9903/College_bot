
from django.urls import path
from chat.views import index, streamlit_chat, courses_view
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', index, name='index'),
    path('streamlit-chat/', streamlit_chat, name='streamlit_chat'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('courses/', courses_view, name='courses'),
    path('courses/aiml/', views.aiml_view, name='aiml'),  
    path('courses/aids/', views.aids_view, name='aids'),
    path('courses/bio/', views.bio_view, name='bio'),
    path('courses/csd/', views.csd_view, name='csd'),
    path('courses/civ/', views.civ_view, name='civ'),
        
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
