from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Opportunity, Application
from .googleLocal import validate_location
from django.conf import settings
from datetime import date
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField

User = get_user_model()

class RegistreSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only = True)
    


    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'user_type',
                   'organization_name', 'mission_statement', 'contact',
                   'skills', 'availability', 'location',      
                 ]
        
        extra_kwargs = {
            'organization_name': {'required': False, 'help_text': 'For organizations only.'},
            'mission_statement': {'required': False, 'help_text': 'For organizations only.'},
            'contact': {'required': False, 'help_text': 'For Anyone.'},
            'skills': {'required': False, 'help_text': 'For volunteers only.'},
            'availability': {'required': False, 'help_text': 'For volunteers only.'},
            'location': {'required': False, 'help_text': 'For volunteers only.'},
        }
        
        
    def create(self,validated_data):
         password = validated_data.pop('password', None)
         location_name = validated_data.get('location', None)

         if location_name:
            formatted_location, lat, lon = validate_location(location_name, api_key=settings.GOOGLE_API_KEY)
            validated_data['location'] = formatted_location

         user = User.objects.create(**validated_data)
         if password:
            user.set_password(password)
         user.save()
         return user
    
    def validate_location(self, location_name):
        
        formatted_location, lat, lon = validate_location(location_name, api_key = settings.GOOGLE_API_KEY)
        if lat is None or lon is None:
            raise serializers.ValidationError("Invalid location name.")
        return formatted_location
    

    #customize output based on user type
    def to_representation(self, instance):
        
        representation = super().to_representation(instance)
        if instance.user_type == 'volunteer':
            representation.pop('organization_name', None)
            representation.pop('mission_statement', None)
        elif instance.user_type == 'organization':
            representation.pop('skills', None)
            representation.pop('availability', None)
            representation.pop('location', None)
        return representation
    
    
    
class NotificationSerializer(serializers.ModelSerializer):

    notifications = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_info', 'notifications']

    @extend_schema_field(CharField())
    def get_user_info(self, obj) -> str:
        return {
            'user_type': obj.user_type,
            'email': obj.email
        }

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_notifications(self, obj):
        if obj.user_type == 'organization':
            return self.get_organization_notifications(obj)
        elif obj.user_type == 'volunteer':
            return self.get_volunteer_notifications(obj)
        return []

    def get_organization_notifications(self, obj):
        notifications = []

        #find opportunities created by this organization
        opportunities = Opportunity.objects.filter(organization = obj)

        for opp in opportunities:
            #get applications attached for this opportunity
            applications = Application.objects.filter(opportunity = opp)
            
            for app in applications:
                #notification message for each application
                notifications.append(
                    f"Volunteer '{app.volunteer.email}' has applied for your opportunity '{opp.title}'. Status: '{app.status}'"
                )

        return notifications


    def get_volunteer_notifications(self, obj):
        notifications = []

        #get applications submitted by the volunteer
        applications =  Application.objects.filter(volunteer = obj)
        for application in applications:
            notifications.append(
                f"Your application for the opportunity '{application.opportunity.title}' is currently '{application.status}'."
            )

        return notifications


    





class TrackingSerializer(serializers.ModelSerializer):
     
    
    opportunities_details = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'user_type', 'opportunities_details']


    #get details of the opportunities
    @extend_schema_field(serializers.ListField(child = serializers.CharField()))
    def get_opportunities_details(self, obj):
        
        opportunities = []
        for application in obj.applications.all():
            opportunity = application.opportunity
            if opportunity:
                opp_data = {
                    'title': opportunity.title,
                    'description': opportunity.description,
                    'hours_spent': self.calculate_hours(opportunity),
                    'feedback': self.get_feedback(opportunity)
                }
                opportunities.append(opp_data)
        return opportunities

    #using 8 hour a day work days hours a calculted from start date to end date or part there of
    def calculate_hours(self, opportunity):
       
        today = date.today()
        start_date = opportunity.start_date
        end_date = opportunity.end_date if opportunity.completed else today

        
        if start_date and start_date <= end_date:
            days_spent = (end_date - start_date).days + 1  

            return days_spent * 8  
        return 0

    #collect feedback from the opportunity endpoint
    #to the fill in the feedback field of the tracking endpoint
    def get_feedback(self, opportunity):
       
        if opportunity.completed:
            return opportunity.feedback
        return None




class OpportunitySerializer(serializers.ModelSerializer):

    applicants = serializers.SerializerMethodField()
    organization = serializers.PrimaryKeyRelatedField(queryset = User.objects.filter(user_type = 'organization'), required = True)

    class Meta:
        model = Opportunity
        fields = ['id', 'title', 'description', 'organization', 'required_skills', 'location',
                  'longitude', 'latitude', 'start_date', 'end_date', 'completed', 'feedback', 'applicants']
        read_only_fields = ['applicants']


    @extend_schema_field(serializers.ListField(child = serializers.CharField()))
    def get_applicants(self, obj):
        #applications associated with this opportunity to add to the applicants methodfield
        applicants = Application.objects.filter(opportunity = obj)
        return [
            {
                'volunteer_email': application.volunteer.email,
                'status': application.status
            }
            for application in applicants if application.volunteer
        ]
    
    #removes these fields if tha user is a volunteer
    def to_representation(self, instance):
        
        request = self.context.get('request')
        representation = super().to_representation(instance)

        if request and request.user.user_type == 'volunteer':
            representation.pop('feedback', None)
            representation.pop('applicants', None)
        
        return representation
    
    #resolver of locations
    def validate_and_format_location(self, validated_data):
       
        location_name = validated_data.get("location")
        if location_name:
            formatted_address, lat, lng = validate_location(location_name, settings.GOOGLE_API_KEY)
            if lat and lng:
                validated_data["location"] = formatted_address
                validated_data["latitude"] = lat
                validated_data["longitude"] = lng
            else:
                raise serializers.ValidationError({"location": "Invalid or unresolvable location."})
        return validated_data

    def create(self, validated_data):
        #logged-in user  is automatically assigned as the organization
        request = self.context.get('request')
        if request and request.user.user_type == 'organization':
            validated_data['organization'] = request.user  
        elif 'organization' not in validated_data:
            raise serializers.ValidationError("Organization is required to create an opportunity.")
        
        validated_data = self.validate_and_format_location(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.validate_and_format_location(validated_data)
        return super().update(instance, validated_data)



class ApplicationSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Application
        fields = ['opportunity','id','status','application_date']
        
       
    def create(self, validated_data):
        #associate the logged-in user as the volunteer
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['volunteer'] = request.user
        else:
            raise serializers.ValidationError({"volunteer": "Only authenticated users can apply."})
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        #only organization that owns the opportunity can update the status field
        request = self.context.get('request')
        if request and request.user.user_type == 'organization':
            
            instance.status = validated_data.get('status', instance.status)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError("You do not have permission to update the status.")