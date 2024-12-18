from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)  
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    owner = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,related_name='owned_users')
    
    USER_TYPE_CHOICES = (
        ('volunteer', 'Volunteer'),
        ('organization', 'Organization'),
    )



    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    #organizations
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    mission_statement = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=100)
    past_projects = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=15, blank=True, null=True)

    #volunteers
    skills = models.TextField(blank=True, null=True)
    preferences = models.CharField(max_length=100)
    availability = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type']  


    def __str__(self):
        return self.email

    
class Opportunity(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    organization = models.ForeignKey(CustomUser, related_name='opportunities', on_delete=models.SET_NULL,null=True)
    required_skills = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    completed = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    volunteer = models.ForeignKey(CustomUser,related_name='applications', on_delete=models.SET_NULL,null=True)
    opportunity = models.ForeignKey(Opportunity, related_name='applications', on_delete=models.SET_NULL,null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    application_date = models.DateTimeField()
   

    def __str__(self):
        return self.volunteer.email + self.opportunity.title + self.status
    
    