from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
import os
from admin_user.models import AdminUser
from brave_lab_project.settings import BASE_DIR

from main_home.models import Anemia, Appointment, ChatRoom, Component, ComponentInformation, Diabetes, Lobby, Test, TestResult

from django.db.models.signals import pre_save, pre_delete
from client.models import Client
from nurse.models import Nurse
from receptionist.models import Receptionist
from auditor.models import Auditor
import joblib
import numpy as np
import os


#######   Tests 

@receiver(post_save, sender=TestResult)
def test_result_created(sender, instance, created , **kwargs):
    result = instance
    evaluation = result.request.appointment.evaluation
    client = result.request.appointment.client
    tests = result.request.tests.all()
    test_names = []
    for test in tests:
        test_name = test.test_offered.name
        test_names.append(test_name)
        
    # Compare the test_names to see if any of them match the name CBC
    if created :
        if 'Complete Blood Count (CBC)' in test_names:
            test = tests.filter(test_offered__name = 'Complete Blood Count (CBC)').first()
            age = evaluation.age
            gender = evaluation.gender
            RBC = test.components.all().filter(info__name='Red Blood Cell Count (RBC)').first().value
            PCV = test.components.all().filter(info__name='Hematocrit (Hct)').first().value
            MCV = test.components.all().filter(info__name='Mean Corpuscular Volume (MCV)').first().value
            MCH = test.components.all().filter(info__name='Mean Corpuscular Hemoglobin (MCH)').first().value
            MCHC = test.components.all().filter(info__name='Mean Corpuscular Hemoglobin Concentration (MCHC)').first().value
            RDW = test.components.all().filter(info__name='Red Cell Distribution Width (RDW)').first().value
            TLC = test.components.all().filter(info__name='White Blood Cell Count (WBC)').first().value
            PLT = test.components.all().filter(info__name='Platelet Count (PLT)').first().value
            HGB = test.components.all().filter(info__name='Hemoglobin (Hb)').first().value
                
            # Load the trained model from the file
            log_reg = joblib.load(os.path.join(BASE_DIR, 'IA_modeles/model-anemia/pythonProject1/trained_model_for_anemia.pkl'))
            #Age,Sex,RBC,PCV,MCV,MCH,MCHC,RDW,TLC,PLT/mm3,HGB
            arr = np.array([age,gender,RBC,PCV,MCV,MCH,MCHC,RDW,TLC,PLT,HGB])
            print(arr)
            reshaped_arr = arr.reshape(1, -1)

            # Load the scaler used for training
            scaler = joblib.load(os.path.join(BASE_DIR, 'IA_modeles/model-anemia/pythonProject1/scaler_for_anemia.pkl'))
            arr_scaled = scaler.transform(reshaped_arr)

            # Make predictions and get probabilities
            predictions = log_reg.predict(arr_scaled)
            prediction = predictions[0]
            probabilities = log_reg.predict_proba(arr_scaled)


            # Extract the probability for the positive class (class 1)
            positive_probability = probabilities[0, 1]

            # Convert the probability to percentage
            positive_percentage = positive_probability * 100
            print(positive_percentage)
            if 0 < positive_percentage <= 100:
                positive_percentage = "{:.2f}".format(positive_percentage)
            else :
                positive_percentage = 0.0

            if prediction == 0 :
                print("Prediction: Negative for Anemia")
                positive=False
            elif prediction == 1 :
                print("Prediction: Positive For Anemia")
                positive=True
                
            print("Positive Probability:", positive_probability)
            print("Positive Percentage:", positive_percentage, "%")
            
            anemia = Anemia(result = result, positive=positive,probability=positive_percentage)
            anemia.save()
            print(anemia)
            
        # gender,age,hypertension,heart_disease,smoking_history,bmi,HbA1c_level,blood_glucose_level  
        if 'Hemoglobin A1C (HbA1c)' in test_names and ( ('Basic Metabolic Panel (BMP)' in test_names)  or  ('Comprehensive Metabolic Panel (CMP)' in test_names) ):
            HA1C_test = tests.filter(test_offered__name = 'Hemoglobin A1C (HbA1c)').first()
            BMP_test = tests.filter(test_offered__name = 'Basic Metabolic Panel (BMP)').first()  
            CMP_test = tests.filter(test_offered__name = 'Comprehensive Metabolic Panel (CMP)').first()  
            
            if BMP_test :
                MP_test = BMP_test 
            elif CMP_test :
                MP_test = CMP_test
                
            
            age = evaluation.age
            gender = evaluation.gender
            hypertension = evaluation.hypertension
            heart_disease = evaluation.heart_disease
            smoking_history = evaluation.smoking_history
            bmi = evaluation.bmi
             

            HbA1c = HA1C_test.components.all().filter(info__name='HbA1c').first().value
            Glucose = MP_test.components.all().filter(info__name='Glucose (GLU)').first().value
                
            # Load the trained model from the file
            log_reg = joblib.load(os.path.join(BASE_DIR, 'IA_modeles/model-diabete/pythonProject2/trained_model_for_diabetes.pkl'))
            # gender,age,hypertension,heart_disease,smoking_history,bmi,HbA1c_level,blood_glucose_level  
            arr = np.array([gender,age,hypertension,heart_disease,smoking_history,bmi,HbA1c,Glucose])
            print(arr)
            reshaped_arr = arr.reshape(1, -1)

            # Load the scaler used for training
            scaler = joblib.load(os.path.join(BASE_DIR, 'IA_modeles/model-diabete/pythonProject2/scaler_for_diabetes.pkl'))
            arr_scaled = scaler.transform(reshaped_arr)

            # Make predictions and get probabilities
            predictions = log_reg.predict(arr_scaled)
            prediction = predictions[0]
            probabilities = log_reg.predict_proba(arr_scaled)


            # Extract the probability for the positive class (class 1)
            positive_probability = probabilities[0, 1]

            # Convert the probability to percentage
            positive_percentage = positive_probability * 100
            print(positive_percentage)
            if 0 < positive_percentage <= 100:
                positive_percentage = "{:.2f}".format(positive_percentage)
            else :
                positive_percentage = 0.0

            if prediction == 0 :
                print("Prediction: Negative for Diabete")
                positive=False
            elif prediction == 1 :
                print("Prediction: Positive For Diabete")
                positive=True
                
            print("Positive Probability:", positive_probability)
            print("Positive Percentage:", positive_percentage, "%")
            
            diabetes = Diabetes(result = result, positive=positive,probability=positive_percentage)
            diabetes.save()
            print(diabetes)
    
        

@receiver(post_save, sender=Test)
def add_components_to_test(sender, instance, created, **kwargs):
    
    if created and instance.test_offered.name == 'Complete Blood Count (CBC)':
        
        component_names = [
            'Red Blood Cell Count (RBC)',
            'Hematocrit (Hct)',
            'Mean Corpuscular Volume (MCV)',
            'Mean Corpuscular Hemoglobin (MCH)',
            'Mean Corpuscular Hemoglobin Concentration (MCHC)',
            'Red Cell Distribution Width (RDW)',
            'White Blood Cell Count (WBC)',
            'Platelet Count (PLT)',
            'Hemoglobin (Hb)',
        ]
        components = []
        for component_name in component_names:
            component_info = ComponentInformation.objects.get(name=component_name)
            component = Component(info=component_info)
            components.append(component)
        Component.objects.bulk_create(components)
        instance.components.add(*components)
        
    if created and instance.test_offered.name == 'Basic Metabolic Panel (BMP)':
        
        component_names = [
            'Glucose (GLU)', 
            'Sodium (Na)',  
            'Potassium (K)', 
            'Calcium (Ca)', 
            'Chloride (Cl)', 
            'Carbon Dioxide (CO2)',  
            'Blood Urea Nitrogen (BUN)', 
            'Creatinine (Cr)', 
        ]
        components = []
        for component_name in component_names:
            component_info = ComponentInformation.objects.get(name=component_name)
            component = Component(info=component_info)
            components.append(component)
        Component.objects.bulk_create(components)
        instance.components.add(*components)
        
    if created and instance.test_offered.name == 'Comprehensive Metabolic Panel (CMP)':
        
        component_names = [
            'Glucose (GLU)',
            'Sodium (Na)', 
            'Potassium (K)',
            'Calcium (Ca)',
            'Chloride (Cl)',
            'Carbon Dioxide (CO2)',
            'Blood Urea Nitrogen (BUN)',
            'Creatinine (Cr)',
            'Albumin (Alb)',
            'Bilirubin (Bili)',  
            'Total Protein Level (TP)', 
            'Alkaline Phosphatase (ALP)', 
            'Alanine Aminotransferase (ALT)', 
            'Aspartate Aminotransferase (AST)',
        ]
        
        components = []
        for component_name in component_names:
            component_info = ComponentInformation.objects.get(name=component_name)
            component = Component(info=component_info)
            components.append(component)
            
        Component.objects.bulk_create(components)
        instance.components.add(*components)
        
    if created and instance.test_offered.name == 'Lipid Panel':
        
        component_names = [
            'Total Cholesterol (TC)',
            'High-Density Lipoprotein (HDL)',
            'Low-Density Lipoprotein (LDL)',
            'Triglyceride (TG)', 
        ]
        components = []
        for component_name in component_names:
            component_info = ComponentInformation.objects.get(name=component_name)
            component = Component(info=component_info)
            components.append(component)
        Component.objects.bulk_create(components)
        instance.components.add(*components)
    
    
    if created and instance.test_offered.name == 'Thyroid Function Tests':
        
        component_names = [
            'Thyroid-Stimulating Hormone (TSH)',
            'Triiodothyronine (T3)', 
            'Thyroxine (T4)', 
        ]
        components = []
        for component_name in component_names:
            component_info = ComponentInformation.objects.get(name=component_name)
            component = Component(info=component_info)
            components.append(component)
        Component.objects.bulk_create(components)
        instance.components.add(*components)
        
        
    if created and instance.test_offered.name == 'Hemoglobin A1C (HbA1c)':
        
        component_names = [
            'HbA1c', 
        ]
        components = []
        for component_name in component_names:
            component_info = ComponentInformation.objects.get(name=component_name)
            component = Component(info=component_info)
            components.append(component)
        Component.objects.bulk_create(components)
        instance.components.add(*components)
        
        
    if created and instance.test_offered.name == 'Coagulation Panel':
        
        component_names = [
            'Prothrombin Time (PT)', 
            'Partial Thromboplastin Time (PTT)', 
            'International Normalized Ratio (INR)',
        ]
        components = []
        for component_name in component_names:
            component_info = ComponentInformation.objects.get(name=component_name)
            component = Component(info=component_info)
            components.append(component)
        Component.objects.bulk_create(components)
        instance.components.add(*components)
        
        
    if created and instance.test_offered.name == 'Vitamin D Levels':
        
        component_names = [
            'Vitamin D', 
        ]
        components = []
        for component_name in component_names:
            component_info = ComponentInformation.objects.get(name=component_name)
            component = Component(info=component_info)
            components.append(component)
        Component.objects.bulk_create(components)
        instance.components.add(*components)
        
        
#######   Documents



def get_all_document_paths():
    # Retrieve all document paths from the Appointment table
    all_documents = Appointment.objects.exclude(document='').values_list('document', flat=True)
    return set(all_documents)


def delete_unused_images():
    # Get all document paths from the database
    all_documents = get_all_document_paths()

    # Get the path of the directory where the images are stored
    image_directory = 'medical_documents/'

    # Get a list of all files in the image directory
    all_files = default_storage.listdir(image_directory)[1]

    # Loop through each file in the directory
    for file_name in all_files:
        file_path = os.path.join(image_directory, file_name)

        # Check if the file path does not exist in the database documents
        if file_path not in all_documents:
            # Delete the file
            default_storage.delete(file_path)


@receiver(post_save, sender=Appointment)
@receiver(post_delete, sender=Appointment)
def handle_appointment_change(sender, instance, **kwargs):
    delete_unused_images()
    
    
######## Profile pictures

def get_all_profile_pic_paths():
    # Retrieve all profile picture paths from the user models
    all_profile_pics = (
        list(Client.objects.exclude(profile_pic='').values_list('profile_pic', flat=True)) +
        list(Nurse.objects.exclude(profile_pic='').values_list('profile_pic', flat=True)) +
        list(Receptionist.objects.exclude(profile_pic='').values_list('profile_pic', flat=True)) +
        list(Auditor.objects.exclude(profile_pic='').values_list('profile_pic', flat=True))+
        list(AdminUser.objects.exclude(profile_pic='').values_list('profile_pic', flat=True))
    )
    return set(all_profile_pics)


def delete_unused_profile_pics():
    # Get all profile picture paths from the database
    all_profile_pics = get_all_profile_pic_paths()

    # Get the path of the directory where the profile pictures are stored
    profile_pic_directory = 'profile_pics/'

    # Get a list of all files in the profile picture directory
    all_files = default_storage.listdir(profile_pic_directory)[1]

    # Loop through each file in the directory
    for file_name in all_files:
        file_path = os.path.join(profile_pic_directory, file_name)

        # Check if the file path does not exist in the database profile pictures
        if file_path not in all_profile_pics:
            # Delete the file
            default_storage.delete(file_path)


@receiver(pre_save, sender=Client)
@receiver(pre_save, sender=Nurse)
@receiver(pre_save, sender=Receptionist)
@receiver(pre_save, sender=Auditor)
@receiver(pre_save, sender=AdminUser)
def handle_user_profile_pic_change(sender, instance, **kwargs):
    if sender.objects.filter(pk=instance.pk).exists() :
        # Retrieve the existing profile picture path
        old_profile_pic_path = sender.objects.get(pk=instance.pk).profile_pic.path
        old_profile_pic = sender.objects.get(pk=instance.pk).profile_pic

        # Check if the existing profile picture is different from the new profile picture
        if old_profile_pic_path != instance.profile_pic.path and old_profile_pic != "default.png" :
            # Delete the old profile picture
            default_storage.delete(old_profile_pic_path)


@receiver(pre_delete, sender=Client)
@receiver(pre_delete, sender=Nurse)
@receiver(pre_delete, sender=Receptionist)
@receiver(pre_delete, sender=Auditor)
@receiver(pre_delete, sender=AdminUser)
def handle_user_profile_pic_deletion(sender, instance, **kwargs):
    # Delete the profile picture when a user is deleted
    profile_pic_path = instance.profile_pic.path
    profile_pic = instance.profile_pic
    if profile_pic != "default.png" :
        default_storage.delete(profile_pic_path)

    # Delete unused profile pictures
    delete_unused_profile_pics()


# Nurse Lobby
@receiver(post_save, sender=Nurse)
def create_nurse_lobby(sender, instance, created, **kwargs):
    if created:
        lobby = Lobby.objects.create(nurse=instance)
        print(lobby.clients)
        
@receiver(pre_delete, sender=Nurse)
def delete_nurse_lobby(sender, instance, **kwargs):
    if instance.lobby:
        instance.lobby.delete()


@receiver(post_save, sender=Nurse)
def create_chat_room(sender, instance, created, **kwargs):
    if created:

        # Create a new chat room
        chat_room = ChatRoom(name=f"Nurse Chat Room {instance.user.id}")

        # Add the nurse and main auditor to the chat room
        chat_room.nurse = instance
        chat_room.auditor = Auditor.objects.all().first()
        chat_room.save()