from rest_framework.test import APITestCase
from service.models import Opportunity, Application
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime,date
from django.utils.timezone import make_aware
from service.serializers import TrackingSerializer, NotificationSerializer



User = get_user_model()

"""TESTS FOR REGISTER ENDPOINT"""

class registration(APITestCase):
    def setUp(self):
        
        self.url = reverse('register')
        self.data = {
            "email": "volunteer@gmail.com",
            "password": "password",
            "user_type": "volunteer",
            "skills": "Coding, chupidness",
            "availability": "Weekends",
            "location": "New York"
        }
        
        self.data_missing_password = {'email': 'user@gmail.com'}
        self.data_invalid_email_field = {'email':'user'}
        self.data_missing_email = {'password':'password'}
    
    
    def test_registration(self):
        
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
       
          

    def test_registration_invalid_or_missing_fields(self):
        
        #test missing password
        response = self.client.post(self.url, self.data_missing_password)
        self.assertEqual( response.status_code, status.HTTP_400_BAD_REQUEST)

        #test missing email
        response = self.client.post(self.url, self.data_missing_email)
        self.assertEqual( response.status_code, status.HTTP_400_BAD_REQUEST)

        #test invalid email field
        response = self.client.post(self.url, self.data_invalid_email_field)
        self.assertEqual( response.status_code, status.HTTP_400_BAD_REQUEST)


"""TESTS FOR LOGIN ENPOINT"""
class login(APITestCase):

    def setUp(self):
        
        #url for obtaining login token
        self.url = reverse('token_obtain_pair')

        #mimic an already existing user object
        self.user = User.objects.create_user(
            email = 'user@gmail.com', 
            password = 'password'
            )
        
        self.data_missing_password = {'email': 'user@gmail.com'}
        self.data_missing_username = {'password': 'password'}
   

        
        

    def test_successfull_login(self):

        #login test object data
        data = {
            'email': 'user@gmail.com',
            'password': 'password'
            }
        
        #post data to url to see if there is a match
        response = self.client.post(self.url, data)
        
        #if respone code matches unit test will pass
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_login(self):

        #test with missing password   
        response = self.client.post(self.url, self.data_missing_password, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('password' in response.data) 


        #test with missing username

        response = self.client.post(self.url, self.data_missing_username, format = 'json' )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('email' in response.data) 



        #test invalid email
        data = {
            'email': 'crap@gamil.com',  
            'password': 'password' 
            }
        

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
   
  

        #test invalid password
        data2 = {
            'email': 'user@gmail.com',  
            'password': 'crap'  
            }
        
        response = self.client.post(self.url, data2)
          
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


"""TESTS FOR opportunity MANAGEMENT"""
class OpportunityCreation(APITestCase):
    def setUp(self):
        #url for creating a new opportunity
        self.url = reverse('opportunity-list-create')  

        #create a test user objects
        self.volunteer = User.objects.create_user(
            email='volunteer@gmail.com',
            password='password',
            user_type='volunteer'
            )

        self.organization = User.objects.create_user(
            email='organization@gmail.com',
            password='password',
            user_type='organization'
            )
        
        self.volunteer_token = RefreshToken.for_user(self.volunteer).access_token
        self.organization_token = RefreshToken.for_user(self.organization).access_token
        

    #test if a volunteer can create an opportunity (they shouldn't)
    def test_opportunity_creation_by_volunteer(self):

        data = {
            "title": "Invalid Opportunity",
            "description": "Volunteers shouldn't create opportunities.",
            "required_skills": "A,B",
            "location": "Anywhere",
            "start_date": "2024-12-25",
            "end_date": "2024-12-30"
        }


        #get/save a login token for the user
        response = self.client.post(self.url, data, HTTP_AUTHORIZATION=f'Bearer {self.volunteer_token}',format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Opportunity.objects.count(), 0)



    def test_opportunity_creation_unauthorized(self):
        
        data = {
            "title": "Unauthorized Opportunity",
            "organization" : "1",
            "description": "This shouldn't be created.",
            "required_skills": "None",
            "location": "Unknown",
            "start_date": "2024-12-25",
            "end_date": "2024-12-30"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Opportunity.objects.count(), 0)



    def test_opportunity_creation_by_organization_authorized(self):
        
        data = {
            "title": "New Opportunity",
            "organization" :  self.organization.id,
            "description": "Description of the opportunity.",
            "required_skills": "A,B",
            "location": "San Francisco",
            "start_date": "2024-12-25",
            "end_date": "2024-12-30"
        }
        response = self.client.post( self.url, data, HTTP_AUTHORIZATION=f'Bearer {self.organization_token}', format='json')
        #print(response.status_code, response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        

"""TESTS FOR Application MANAGEMENT"""
class ApplicationCreation(APITestCase):
    def setUp(self):
        #url for creating a new opportunity
        self.url = reverse('application-list-create')  

        #create a test user objects
        self.volunteer = User.objects.create_user(
            email='volunteer@gmail.com',
            password='password',
            user_type='volunteer'
            )

        self.organization = User.objects.create_user(
            email='organization@gmail.com',
            password='password',
            user_type='organization'
            )
        
        self.volunteer_token = RefreshToken.for_user(self.volunteer).access_token
        self.organization_token = RefreshToken.for_user(self.organization).access_token
        
        #create a sample Opportunity
        self.opportunity = Opportunity.objects.create(
            title="Sample Opportunity",
            description="A description for a sample opportunity",
            location="New York",
            start_date = "2024-12-25",
            end_date = "2024-12-30",
            organization=self.organization  
        )
    
        

    def test_application_creation_by_volunteer_authorized(self):

        data = {
            "volunteer" : self.volunteer.id,
            "opportunity" : self.opportunity.id,
            "application_date": "2024-12-25"
        }


        #get/save a login token for the user
        response = self.client.post(self.url, data, HTTP_AUTHORIZATION=f'Bearer {self.volunteer_token}',format='json')
        print(response.status_code, response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        


class TrackingSerializerTest(APITestCase):
    def setUp(self):
        #create a test user
        self.user = User.objects.create_user(
            email='volunteer@gmail.com',
            password='password',
            user_type='volunteer'
        )

        #create opportunities
        self.opportunity1 = Opportunity.objects.create(
            title="Tree Planting",
            description="Plant trees in the park.",
            start_date=date(2024, 12, 25), 
            end_date=date(2024, 12, 30),
            completed=True,
            feedback="Great work!"
        )

 

        #get rid of timezone-aware datetime warning for application_date
        application_date = make_aware(datetime(2024, 12, 24))

        #applications for sample opportunites
        Application.objects.create(volunteer=self.user, opportunity=self.opportunity1,application_date=application_date)
        

    def test_tracking_serializer(self):
        #serialize the user data
        serializer = TrackingSerializer(instance=self.user)
        data = serializer.data

        #test user fields
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['user_type'], self.user.user_type)

        #test opportunities details
        opportunities = data['opportunities_details']


        #test details of the first opportunity
        opportunity1_data = next(o for o in opportunities if o['title'] == "Tree Planting")
        self.assertEqual(opportunity1_data['title'], "Tree Planting")
        self.assertEqual(opportunity1_data['description'], "Plant trees in the park.")
        self.assertEqual(opportunity1_data['hours_spent'], 6 * 8)  
        self.assertEqual(opportunity1_data['feedback'], "Great work!")

      



class NotificationSerializerTest(APITestCase):

    def setUp(self):
        #create organization user
        self.organization_user = get_user_model().objects.create_user(
            email='organization@gmail.com',
            password='password',
            user_type='organization'
        )

        #create volunteer user
        self.volunteer_user = get_user_model().objects.create_user(
            email='volunteer@gmail.com',
            password='password',
            user_type='volunteer'
        )

        #create an opportunity for the organization
        self.opportunity = Opportunity.objects.create(
            title="Beach Cleanup",
            description="Help clean the beach.",
            start_date=make_aware(datetime(2024, 12, 25)),#use make_aware to get rid of timezone warning
            end_date=make_aware(datetime(2024, 12, 30)),
            organization=self.organization_user
        )

        #create application for the volunteer
        self.application = Application.objects.create(
            volunteer=self.volunteer_user,
            opportunity=self.opportunity,
            application_date=make_aware(datetime(2024, 12, 24)),
            status='pending' 
        )

    def test_notification_for_organization(self):
       
        serializer = NotificationSerializer(instance=self.organization_user)
        data = serializer.data

        #test that user info is correct
        self.assertEqual(data['user_info']['user_type'], 'organization')
        self.assertEqual(data['user_info']['email'], 'organization@gmail.com')

        #test that notifications are correctly generated
        notifications = data['notifications']
        self.assertIn("Volunteer 'volunteer@gmail.com' has applied for your opportunity 'Beach Cleanup'. Status: 'pending'", notifications)

    def test_notification_for_volunteer(self):
        
        serializer = NotificationSerializer(instance=self.volunteer_user)
        data = serializer.data

        #test that user info is correct
        self.assertEqual(data['user_info']['user_type'], 'volunteer')
        self.assertEqual(data['user_info']['email'], 'volunteer@gmail.com')

        #test that the correct notification is generated for the volunteer
        notifications = data['notifications']

        #test for the correct status
        self.assertIn("Your application for the opportunity 'Beach Cleanup' is currently 'pending'.", notifications)



"""TESTING VIEWS"""
class RegisterViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('register') 
        self.valid_data = {
            'email': 'newuser@gmail.com',
            'password': 'password',
            'user_type': 'volunteer'
        }
        self.invalid_data = {
            'email': 'someemail', 
            'password': 'short',  
            'user_type': 'volunteer',
        }

    def test_register_user_successful(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        

    def test_register_user_invalid_email(self):
        response = self.client.post(self.url, self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)




class UserProfileDetailViewTest(APITestCase):

    def setUp(self):
        #Create test users
        self.user = User.objects.create_user(
            email='user@gmail.com',
            password='password',
            user_type='volunteer'
        )
        
        #get authentication
        self.token = RefreshToken.for_user(self.user).access_token
        
       
        self.url = reverse('user-profile')  

    def test_get_user_profile(self):
        #test  user can retrieve their own profile

        response = self.client.get(self.url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@gmail.com')
        self.assertEqual(response.data['user_type'], 'volunteer')

    def test_update_user_profile(self):
        #test user can update their own profile

       
        updated_data = {
            'email': 'updateduser@gmail.com',
            'password': 'newpassword', 
            'user_type': 'volunteer'
        }

       
        response = self.client.put(self.url, updated_data, HTTP_AUTHORIZATION=f'Bearer {self.token}', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #check that the user’s email was updated
        self.user.refresh_from_db()  #refresh the user from the db
        self.assertEqual(self.user.email, 'updateduser@gmail.com')

    def test_update_user_profile_unauthorized(self):
        #test that a non-authenticated user cannot update the profile

       
        updated_data = {
            'email': 'updateduser@gmail.com',
            'password': 'newpassword',
            'user_type': 'volunteer'
        }

        #Make a PUT request without authentication
        response = self.client.put(self.url, updated_data, format='json')

       
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)






class TrackingDetailViewTest(APITestCase):
    def setUp(self):
        #volunteer user
        self.volunteer_user = User.objects.create_user(
            email='volunteer@gmail.com',
            password='password',
            user_type='volunteer'
        )
        
        #organization user 
        self.organization_user = User.objects.create_user(
            email='organization@gmail.com',
            password='password',
            user_type='organization'
        )

        self.url = reverse('tracking-detail')
        
        self.volunteer_token = RefreshToken.for_user(self.volunteer_user).access_token

        

    def test_retrieve_tracking_details(self):
       
        response = self.client.get(self.url, HTTP_AUTHORIZATION=f'Bearer {self.volunteer_token}')
        
        self.assertEqual(response.status_code,status.HTTP_200_OK)

        tracks = response.data
        self.assertIn('email', tracks)
        self.assertIn('user_type', tracks)
        self.assertIn('opportunities_details', tracks)

        
        self.assertEqual(tracks['email'], self.volunteer_user.email)
        self.assertEqual(tracks['user_type'], self.volunteer_user.user_type)
        self.assertIsInstance(tracks['opportunities_details'], list)
        

    def test_access_denied_for_unauthenticated_user(self):
       
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)






class OpportunityListCreateViewTest(APITestCase):
    
    def setUp(self):

        self.url = reverse('opportunity-list-create')


        #organization user
        self.organization_user = get_user_model().objects.create_user(
            email='organization@gmail.com',
            password = 'password',
            user_type = 'organization'
        )
        
        #volunteer user
        self.volunteer_user = get_user_model().objects.create_user(
            email = 'volunteer@gmail.com',
            password = 'password',
            user_type = 'volunteer'
        )

        #organization user
        self.opportunity  =  Opportunity.objects.create(
            title = "Beach Cleanup",
            description = "Help clean the beach.",
            start_date = make_aware(datetime(2024, 12, 25)),
            end_date = make_aware(datetime(2024, 12, 30)),
            organization = self.organization_user,
            latitude = 40.7128,  
            longitude = -74.0060  
        )
        
       
        self.organization_token = RefreshToken.for_user(self.organization_user).access_token
        
       
        

    def test_create_opportunity(self):
        
        
        data = {
            'title': 'Park Cleanup',
            'description': 'Help clean the park.',
            'organization': self.organization_user.id,
            'required_skills' : 'stuff',
            'location': "New York, NY, USA",
            'longitude': -74.0059728,
            'latitude': 40.7127753,
            'start_date': '2024-12-20',
            'end_date': '2024-12-25'
        }

        
        
        
        response = self.client.post(self.url,data, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}', format = 'json')

        #test opportunity is created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
       

    def test_filter_opportunities_by_date_range(self):
       
        response = self.client.get(self.url, {'start_date': '2024-12-20', 'end_date': '2024-12-30'}, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}', format = 'json')

        #make sure filtered opportunities are correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        opportunities = response.data
        self.assertGreater(len(opportunities), 0)  

    def test_filter_opportunities_by_skills(self):
        
        response = self.client.get(self.url, {'skills': 'gardening'}, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}', format = 'json')

        #make sure filtered opportunities are correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        opportunities = response.data
        self.assertGreater(len(opportunities), 0)  

    def test_filter_opportunities_by_location(self):
       
        response = self.client.get(self.url, {'location': 'New York', 'radius': 50}, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}', format = 'json')

        #test location filtering works
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        opportunities = response.data
        self.assertGreater(len(opportunities), 0) 

    def test_list_opportunities(self):
       
        response = self.client.get(self.url, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}', format = 'json')

        #test if there are opportunities
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        opportunities = response.data
        self.assertGreater(len(opportunities), 0) 






class OpportunityDetailViewTest(APITestCase):

    def setUp(self):
        #organization user
        self.organization_user = User.objects.create_user(
            email = 'organization@gmail.com',
            password = 'password',
            user_type = 'organization'
        )

        #volunteer user
        self.volunteer_user = User.objects.create_user(
            email='volunteer@gmail.com',
            password = 'password',
            user_type = 'volunteer'
        )

        #opportunity
        self.opportunity = Opportunity.objects.create(
            title = "Beach Cleanup",
            description = "Help clean the beach.",
            location = "New York, NY, USA",
            latitude = 40.7128,  
            longitude = -74.0060,
            start_date = make_aware(datetime(2024, 12, 25)),
            end_date = make_aware(datetime(2024, 12, 30)),
            organization = self.organization_user
        )

        #tokens
        self.organization_token = RefreshToken.for_user(self.organization_user).access_token
        self.volunteer_token = RefreshToken.for_user(self.volunteer_user).access_token

       
        self.url = reverse('opportunity-detail', args = [self.opportunity.id])

    def test_retrieve_opportunity(self):
        
        response = self.client.get(self.url, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.opportunity.title)
        self.assertEqual(response.data['description'], self.opportunity.description)

    def test_update_opportunity(self):
        
        update_data = {
            'title': "Updated Beach Cleanup",
            'description': "Updated description.",
            'organization': self.organization_user.id,
            'location': "Miami Beach", 
            'required_skills': "Cleaning, Teamwork", 
            'start_date': '2024-12-26',
            'end_date': '2024-12-31'
        }
        response = self.client.put(self.url, update_data, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}', format = 'json')
        print("Response data:", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], update_data['title'])
        self.assertEqual(response.data['description'], update_data['description'])

    def test_delete_opportunity(self):
        
        response = self.client.delete(self.url, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Opportunity.objects.filter(id = self.opportunity.id).exists())

    def test_retrieve_opportunity_as_volunteer(self):
        #volunteer user should not be able to access opportunity details
        response = self.client.get(self.url, HTTP_AUTHORIZATION = f'Bearer {self.volunteer_token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_opportunity_as_volunteer(self):
        #volunteer user should not be able to update the opportunity
        update_data = {
            'title': "Unauthorized Update",
            'description': "Unauthorized description.",
        }

        response = self.client.put(self.url, update_data, HTTP_AUTHORIZATION = f'Bearer {self.volunteer_token}', format = 'json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_opportunity_as_volunteer(self):
        #volunteer user should not be able to delete the opportunity
        response = self.client.delete(self.url, HTTP_AUTHORIZATION = f'Bearer {self.volunteer_token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)







class ApplicationListCreateViewTest(APITestCase):
    
    def setUp(self):
        #organization user
        self.organization_user = User.objects.create_user(
            email = 'organization@gmail.com',
            password = 'password',
            user_type = 'organization'
        )
        
        #volunteer user
        self.volunteer_user = User.objects.create_user(
            email = 'volunteer@gmail.com',
            password = 'password',
            user_type = 'volunteer'
        )

        #opportunity for the organization user
        self.opportunity = Opportunity.objects.create(
            title = "Beach Cleanup",
            description = "Help clean the beach.",
            start_date = make_aware(datetime(2024, 12, 25)),
            end_date = make_aware(datetime(2024, 12, 30)),
            organization = self.organization_user
        )

        #application for the volunteer
        self.application = Application.objects.create(
            volunteer = self.volunteer_user,
            opportunity = self.opportunity,
            application_date = make_aware(datetime(2024, 12, 24)),
            status = 'pending'
        )

        #tokens for the users
        self.organization_token = RefreshToken.for_user(self.organization_user).access_token
        self.volunteer_token = RefreshToken.for_user(self.volunteer_user).access_token

       
        self.url = reverse('application-list-create')

    def test_list_applications_as_volunteer(self):
        #volunteer should be able to list their applications
        response = self.client.get(self.url, HTTP_AUTHORIZATION = f'Bearer {self.volunteer_token}')
        applications = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
         
        self.assertEqual(applications[0]['id'], self.application.id)
        self.assertEqual(applications[0]['status'], 'pending')
        self.assertEqual(applications[0]['opportunity'], self.opportunity.id)

    def test_list_applications_as_organization(self):
        #organization should not be authorized to list applications
        response = self.client.get(self.url, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) #IsVolunteer permission

    def test_create_application_as_volunteer(self):
        #volunteer should be able to create a new application
        data  =  {
            'opportunity': self.opportunity.id,
            'application_date': '2024-12-20'
        }
        response = self.client.post(self.url, data, HTTP_AUTHORIZATION = f'Bearer {self.volunteer_token}', format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['opportunity'], self.opportunity.id)
        self.assertEqual(response.data['status'], 'pending')

        #mak sure application is created in the database
        new_application = Application.objects.get(id = response.data['id'])
        self.assertEqual(new_application.volunteer, self.volunteer_user)

    def test_create_application_as_organization(self):
        #organization should not be allowed to create an application
        data = {
            'opportunity': self.opportunity.id,
            'application_date': '2024-12-20'
        }
        response = self.client.post(self.url, data, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}', format = 'json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  #IsVolunteer permission




class ApplicationDetailViewTest(APITestCase):
    
    def setUp(self):
        #organization user
        self.organization_user = User.objects.create_user(
            email = 'organization@gmail.com',
            password = 'password',
            user_type = 'organization'
        )
        
        #volunteer user
        self.volunteer_user = User.objects.create_user(
            email = 'volunteer@gmail.com',
            password = 'password',
            user_type = 'volunteer'
        )

        #opportunity for the organization user
        self.opportunity = Opportunity.objects.create(
            title = "Beach Cleanup",
            description = "Help clean the beach.",
            start_date = make_aware(datetime(2024, 12, 25)),
            end_date = make_aware(datetime(2024, 12, 30)),
            organization = self.organization_user
        )

        #application for the volunteer
        self.application = Application.objects.create(
            volunteer = self.volunteer_user,
            opportunity = self.opportunity,
            application_date = make_aware(datetime(2024, 12, 24)),
            status = 'pending'
        )

        #tokens for the users
        self.organization_token = RefreshToken.for_user(self.organization_user).access_token
        self.volunteer_token = RefreshToken.for_user(self.volunteer_user).access_token

       
        self.url = reverse('application-detail', kwargs = {'pk': self.application.id})

    def test_retrieve_application_as_organization(self):
        #organization user should be able to retrieve the application
        response = self.client.get(self.url, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.application.id)
        self.assertEqual(response.data['status'], 'pending')

    def test_retrieve_application_as_volunteer(self):
        #volunteer should not be authorized to retrieve the application
        response = self.client.get(self.url, HTTP_AUTHORIZATION = f'Bearer {self.volunteer_token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  

    def test_update_application_status_as_organization(self):
        #organization user should be able to update the application status
        updated_data = {'status': 'accepted'}
        response = self.client.patch(self.url, updated_data, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}', format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'accepted')

        #test if status is updated in the database
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'accepted')

    def test_update_application_status_as_volunteer(self):
        #volunteer should not be allowed to update the application
        updated_data = {'status': 'accepted'}
        response = self.client.patch(self.url, updated_data, HTTP_AUTHORIZATION = f'Bearer {self.volunteer_token}', format = 'json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  

    def test_delete_application_as_organization(self):
        #organization user should be able to delete the application
        response = self.client.delete(self.url, HTTP_AUTHORIZATION = f'Bearer {self.organization_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  

        #make sure application is deleted
        self.assertFalse(Application.objects.filter(id = self.application.id).exists())

    def test_delete_application_as_volunteer(self):
        #volunteer should not be allowed to delete the application
        response = self.client.delete(self.url, HTTP_AUTHORIZATION = f'Bearer {self.volunteer_token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  
