from rest_framework import permissions

#permission for only creators of a specific object can edit it
class IsOwnerReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        print(f"Request User: {request.user}, Opportunity Organization: {obj.organization}")
        return obj.organization == request.user
    
class IsOrganization(permissions.BasePermission):
   
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.user_type == 'organization'
        return False

#permission to restrict posts and updates to only memebers of an organization   
class IsOrganizationReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
       
        if request.method in permissions.SAFE_METHODS:
            return True
        
        #check if the user is authenticated and is an organization
        if request.user and request.user.is_authenticated:
            return request.user.user_type == 'organization'
        
        return False




#permission to restrict access to only volunteers
class IsVolunteer(permissions.BasePermission):
     def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'volunteer'