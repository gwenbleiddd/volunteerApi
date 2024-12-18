from rest_framework import generics
from django.contrib.auth import get_user_model
from django.shortcuts import render
from .models import Opportunity, Application, CustomUser
from .serializers import RegistreSerializer, OpportunitySerializer, ApplicationSerializer, TrackingSerializer, NotificationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsOwnerReadOnly, IsVolunteer, IsOrganizationReadOnly, IsOrganization
from .googleLocal import validate_location,haversine
from django.conf import settings
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from typing import List
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


User = get_user_model()

def home(request):
    
    return render(request,'home.html')


class RegisterView(generics.CreateAPIView):
    
  
    queryset = CustomUser.objects.all().order_by('id')            
    serializer_class = RegistreSerializer
    permission_classes = [AllowAny]  
    

class UserProfileDetailView(generics.RetrieveUpdateAPIView):

    serializer_class = RegistreSerializer
    permission_classes = [IsAuthenticated, IsOwnerReadOnly]

    def get_object(self):
        return self.request.user #get the current logged-in user

class NotificationDetailView(generics.RetrieveAPIView):
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user #get the current logged-in user


class TrackingDetailView(generics.RetrieveAPIView):
    
    serializer_class = TrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user #get the current logged-in user


@extend_schema(responses={200: OpportunitySerializer})
class OpportunityListCreateView(generics.ListCreateAPIView):
    
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated,IsOrganizationReadOnly]
    def get_queryset(self) -> List[Opportunity]:
        queryset = Opportunity.objects.all().order_by('id')
        #filter by skills
        skills = self.request.query_params.get('skills')
        if skills:
            queryset = queryset.filter(required_skills__icontains = skills)

        #filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                Q(start_date__gte=start_date) & Q(end_date__lte = end_date)
            )

        #filter by location
        location = self.request.query_params.get('location')
        radius = self.request.query_params.get('radius', 50)  #starting point for radius
        if location:
            formatted_address, lat, lng = validate_location(location, settings.GOOGLE_API_KEY)
            if lat and lng:
                queryset = [
                    opp for opp in queryset
                    if haversine(lat, lng, opp.latitude, opp.longitude) <= float(radius)
                ]

        return queryset
    
    

class OpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Opportunity.objects.all().order_by('id') 
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated, IsOrganization]
    
    

class ApplicationListCreateView(generics.ListCreateAPIView):
    
    queryset = Application.objects.all().order_by('id')
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated,IsVolunteer]  
    
   
    
class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Application.objects.all().order_by('id')
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated,IsOrganization]
    
