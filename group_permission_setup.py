from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from client.models import Client
from nurse.models import Nurse
from auditor.models import Auditor
from receptionist.models import Receptionist
from django.db import IntegrityError
# Define the models and permissions
models = [
    {'group_name':'client'      ,'model': Client        , 'codename': 'view_client'},
    {'group_name':'nurse'       ,'model': Nurse         , 'codename': 'view_nurse'},
    {'group_name':'receptionist','model': Receptionist  , 'codename': 'view_receptionist'},
    {'group_name':'auditor'     ,'model': Auditor       , 'codename': 'view_auditor'},
]

# Create the groups
for model in models:
    try:
        group = Group.objects.create(name=model['group_name'])
        
        content_type = ContentType.objects.get_for_model(model['model'])
        permission = Permission.objects.get(content_type=content_type, codename=model['codename'])
        group.permissions.add(permission)
    
        print(f"Group {model['group_name']} created successfully!")
    except IntegrityError:
        print(f"Group {model['group_name']} already exists!")
            
        
# Run command :
    # python manage.py shell < group_permission_setup.py
