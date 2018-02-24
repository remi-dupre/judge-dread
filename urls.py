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


from judge.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home),
    path('creation/', creation),
    path('problem/<int:problem_id>/', problem_display),
    path(
        'problem/<int:problem_id>/edit',
        problem_admin,
        name = 'problem_admin'
    ),
    path(
        'problem/<int:problem_id>/<slug:lang>/delete',
        description_delete,
        name ='description_delete'
    ),
    path(
        'problem/<int:problem_id>/<slug:lang>/edit',
        description_edit,
        name ='description_edit'
    )
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
