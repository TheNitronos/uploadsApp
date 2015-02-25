from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from uploads import views



urlpatterns = patterns('',
    url(r'^base/', views.base, name='base'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    
    #upload d'image quelconque
    url(r'^upload/', views.upload, name='upload'),
    
    #affichage des images
    url(r'imagesAll/', views.uploaded, name='uploaded'),
    url(r'imageDetail/(?P<imageId>\w+)', views.detail_uploaded, name='detail_uploaded'),
    
    #suppression d'image et modifications d'images
    url(r'delete/(?P<imageId>\w+)', views.delete, name='delete'),
    url(r'modify/(?P<imageId>\w+)', views.modify, name='modify'),
)



