from django.urls import path
from .views import (RegisterView,UserProfileDetailView, 
                    OpportunityListCreateView, OpportunityDetailView,
                      ApplicationListCreateView, ApplicationDetailView, TrackingDetailView, NotificationDetailView)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
   
)

urlpatterns = [
   path('token/',TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
   path('token/refresh/',TokenRefreshView.as_view(), name = 'token_refresh'),
   path('register/', RegisterView.as_view(), name = 'register'),
   path('profile/', UserProfileDetailView.as_view(), name = 'user-profile'),
   path('opportunities/', OpportunityListCreateView.as_view(), name = 'opportunity-list-create'),
   path('opportunities/<int:pk>/', OpportunityDetailView.as_view(), name = 'opportunity-detail'),
   path('applications/', ApplicationListCreateView.as_view(), name =  'application-list-create'),
   path('applications/<int:pk>/', ApplicationDetailView.as_view(), name =  'application-detail'),
   path('tracking/', TrackingDetailView.as_view(), name =  'tracking-detail'),
   path('notifications/', NotificationDetailView.as_view(), name =  'notification-detail')
]
