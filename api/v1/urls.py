# qubitgyanpro\api\v1\urls.py
from django.urls import path, include

urlpatterns = [
    path('student/', include('api.v1.student.urls')),
    path('staff/', include('api.v1.staff.urls')),
    path('admin/', include('api.v1.admin.urls')),
    path('public/', include('api.v1.public.urls')),
]