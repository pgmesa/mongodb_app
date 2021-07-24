"""configs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from server.server import *

urlpatterns = [
    path('admin/', admin.site.urls),
    # errors
    path('error/', error),
    # dbs
    path('', home, name="home"),
    path('add/', add_db),
    path('update/<db>', update_db),
    path('delete/<db>', delete_db),
    # collections
    path('display/<db>', display_collections),
    path('add/<db>', add_collection),
    path('doc_model/<db>/<collection>', create_doc_model),
    path('update/<db>/<collection>', update_collection),
    path('delete/<db>/<collection>', delete_collection),
    # documents
    path('display/<db>/<collection>', display_documents),
    path('add/<db>/<collection>', add_document),
    path('update/<db>/<collection>/<doc_id>', update_document),
    path('delete/<db>/<collection>/<doc_id>', delete_document),
    path('filter/<db>/<collection>', filter_documents),
    path('sort/<db>/<collection>', sort_documents),
]
