"""judge_dread URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

<<<<<<< HEAD
from judge_dread.views import home,problem,creation
=======
from judge.views import home,problem
>>>>>>> 5d3846ba4bfe7d4ea961a8521381a644a5ad3e5b

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home),
    path('problem/', problem),
    path('creation/', creation)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
