from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from client.models import Client
from nurse.models import Nurse
from auditor.models import Auditor
from receptionist.models import Receptionist
from django.db import IntegrityError


try:
    user = User.objects.create_user(username="client1",password="admin987",first_name='Ahmed',last_name='Amoukrane',email="ahmed.amoukrane@gmail.com")
    group = Group.objects.get(name="client")
    group.user_set.add(user)
    Client.objects.create(user=user,phone_number='0712548256',gender='M',address='Constantine, khroub',policy=True,date_of_birth="2002-07-10")
    print(f'Client {user.username} created successfully!')
except IntegrityError :
    print(f'failed to create Client')
try:
    user = User.objects.create_user(username="nurse1",password="admin987",first_name='Adam',last_name='Bendjamaa',email="adam.bendjamaa@gmail.com")
    group = Group.objects.get(name="nurse")
    group.user_set.add(user)
    Nurse.objects.create(user=user,phone_number='0712548256',gender='M',address='Setif, el eulma',date_of_birth="2003-03-08")
    print(f'Nurse {user.username} created successfully!')
except IntegrityError :
    print(f'failed to create Nurse')
try:
    user = User.objects.create_user(username="receptionist1",password="admin987",first_name='Farouk',last_name='Rahal',email="farouk.rahal@gmail.com")
    group = Group.objects.get(name="receptionist")
    group.user_set.add(user)
    Receptionist.objects.create(user=user,phone_number='0712548256',gender='M',address='Setif, setif',date_of_birth="2001-05-11")
    print(f'Receptionist {user.username} created successfully!')
except IntegrityError :
    print(f'failed to create Receptionist')
try:
    user = User.objects.create_user(username="auditor1",password="admin987",first_name='Rami',last_name='Mammari',email="rami.mammari@gmail.com")
    group = Group.objects.get(name="auditor")
    group.user_set.add(user)
    Auditor.objects.create(user=user,phone_number='0712548256',gender='M',address='Batna, mahther',date_of_birth="1982-01-21")
    print(f'Auditor {user.username} created successfully!')
except IntegrityError :
    print(f'failed to create Auditor')


# Run command :
    # python manage.py shell < insert_default_data.py