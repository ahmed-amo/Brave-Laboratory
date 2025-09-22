from datetime import timedelta, timezone,date
from decimal import Decimal
from django.db import models
from django.forms import ValidationError
from auditor.models import Auditor
from client.models import Client
from nurse.models import Nurse
from receptionist.models import Receptionist
from django.utils import timezone
from django.db.models import Sum,Count,Avg
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth


# Get the current time in Algeria timezone


# Create your models here.

    

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    nurse = models.OneToOneField(Nurse, on_delete=models.CASCADE)
    auditor = models.ForeignKey(Auditor, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From: {self.sender.username} | To: {self.receiver.username}"
    
    
class Complaint(models.Model):
    TOPIC_CHOICES = [
        ('Billing', 'Billing'),
        ('Customer Service', 'Customer Service'),
        ('Facilities', 'Facilities'),
        ('Quality of Service', 'Quality of Service'),
        ('Other', 'Other'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return f"Complaint #{self.id}"

    class Meta:
        db_table = 'complaint'
        


class Laboratory(models.Model):
    name = models.CharField(max_length=45, primary_key=True)
    location = models.CharField(max_length=45)
    description = models.CharField(max_length=45)

    class Meta:
        db_table = 'laboratory'
        verbose_name_plural = 'Laboratories'

    @property
    def tests_made(self):
        return Test.objects.filter().count()
    
    def calculate_monthly_revenue(self):
        current_month = timezone.now().month
        current_year = timezone.now().year
        invoices = Invoice.objects.filter(laboratory=self, creation_time__month=current_month, creation_time__year=current_year)
        total_revenue = invoices.aggregate(total=Sum('total_price'))['total']
        monthly_revenue, _ = MonthlyRevenue.objects.get_or_create(laboratory=self, month=current_month, year=current_year)
        monthly_revenue.revenue = total_revenue or 0
        monthly_revenue.save()

    def get_average_monthly_revenue(self):
        total_revenue = MonthlyRevenue.objects.filter(laboratory=self).aggregate(total=Sum('revenue'))['total']
        months_count = MonthlyRevenue.objects.filter(laboratory=self).count()
        return total_revenue / months_count if months_count else 0

    def __str__(self):
        return self.name
    
class MonthlyRevenue(models.Model):
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'monthly_revenue'

    def __str__(self):
        return f"{self.laboratory} - {self.month}/{self.year}"
        
class ComponentInformation(models.Model):
    name = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=45, null=True, blank=True)
    low_male_range = models.FloatField(null=True, blank=True)
    high_male_range = models.FloatField(null=True, blank=True)
    low_female_range = models.FloatField(null=True, blank=True)
    high_female_range = models.FloatField(null=True, blank=True)
    
    class Meta:
            db_table = 'component_info'
            verbose_name_plural = 'Component Info'
    
    def __str__(self):
        return self.name
    
class Component(models.Model):
    info = models.ForeignKey(ComponentInformation, on_delete=models.CASCADE)
    value = models.FloatField(null=True,blank=True)

    class Meta:
        db_table = 'component'
        
        
    def __str__(self):
        return f'{self.info.name} value:{self.value}'

class TestOffered(models.Model):
    name = models.CharField(max_length=50,unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    urgent = models.BooleanField(default=False)

    class Meta:
        db_table = 'test_offered'
        verbose_name_plural = 'Offered Tests'
        
    def __str__(self):
        return self.name
            
class Test(models.Model):
    test_offered = models.ForeignKey(TestOffered,on_delete=models.CASCADE)
    components = models.ManyToManyField(Component,blank=True)
    value = models.CharField(max_length=100,blank=True,null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    

    class Meta:
            db_table = 'test'
            verbose_name_plural = 'Tests Preformed'
            
    def __str__(self):
        return self.test_offered.name
    
class BloodBank(models.Model):
    MAX_SAMPLE_CAPACITY_CHOICES = [
        (500, '500'),
        (400, '400'),
        (300, '300'),
        (200, '200'),
    ]

    codename = models.CharField(max_length=10)
    capacity = models.IntegerField(choices=MAX_SAMPLE_CAPACITY_CHOICES)

    def __str__(self):
        return f"Blood Bank {self.codename} - Capacity: {self.capacity} samples"

    def count(self):
        return self.blood_samples.count()
    
    def is_full(self):
        sample_count = self.blood_samples.count()
        return sample_count >= self.capacity

    
class BloodSample(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    quantity = models.FloatField()
    unit = models.CharField(max_length=2, default="mL")
    submission_date = models.DateTimeField(auto_now=True)
    blood_bank = models.ForeignKey(BloodBank, related_name='blood_samples', on_delete=models.CASCADE)

    def __str__(self):
        return f"Blood Sample #{self.id} - {self.client.user.username} - Type: {self.blood_type}"

 
 
def validate_date_not_past(date):
    if date < timezone.now().date():
        # dont allow dates from the past
        raise ValidationError('The date cannot be in the past.')
    elif Appointment.objects.filter(date=date).count() >= 50:
        # Don't allow more than 50 appointments per day
        raise ValidationError("Sorry, no more appointments available on this day. Max is 50 per day.")
    
class MedicalDocument(models.Model):
    
    image = models.ImageField(upload_to='medical_documents')
 
    class Meta:
        db_table = 'medical_document'
           
class Appointment(models.Model):
    
    UPCOMING = 'Upcoming'
    TOMORROW = 'Tommorow'
    TODAY = 'Today'
    OVERDUE = 'Overdue'
    STATUS_CHOICES = [
        (UPCOMING, 'Upcoming'),
        (TOMORROW, 'Tommorow'),
        (TODAY, 'Today'),
        (OVERDUE, 'Overdue'),
    ]
    
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    tests_requested = models.ManyToManyField(TestOffered, blank=True) 
    date = models.DateField(validators=[validate_date_not_past])
    description = models.CharField(max_length=1000,blank=True)
    document = models.ImageField(null=True,blank=True,upload_to='medical_documents')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    arrived = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    performed = models.BooleanField(default=False)
    urgent = models.BooleanField(default=False)

    class Meta:
        db_table = 'appointment'
        
    def __str__(self):
        return f"Appointment #{self.id}"
    
    @property
    def cancelable(self):
        time_difference = self.date - timezone.now().date()
        return time_difference.days
        
    @property
    def status(self):
        today = timezone.now().date()
        
        
        if self.date == today:
            return self.TODAY
        elif self.date == today + timezone.timedelta(days=1):
            return self.TOMORROW
        elif self.date > today:
            return self.UPCOMING
        else:
            return self.OVERDUE
        
    @property    
    def check_overdue(self):
        if self.status == self.OVERDUE : 
            self.cancelled = True
            return 1
        return 0
   
   
class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    appointment_fee = models.DecimalField(max_digits=10, decimal_places=2,default=5.00)
    tests_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    nurse_tests_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payed_appointment_fee = models.BooleanField(default=False)
    payed_tests_fee = models.BooleanField(default=False)
    payed_nurse_tests_fee = models.BooleanField(default=False)
    total_amount_payed = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)

    def __str__(self):
        return f"Payment for {self.appointment}"
    
    def save(self, *args, **kwargs):
        if self.tests_fee == 0.00:
            self.tests_fee = self.appointment.total_price
        super().save(*args, **kwargs)
   
class Lobby(models.Model):
    nurse = models.OneToOneField(Nurse, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Appointment, blank=True)
    
    class Meta:
        verbose_name_plural = 'Lobbies'
        
    def __str__(self):
        return f"Lobby: {self.nurse}"
    
    
       
class AnalysisRequest(models.Model):
    PENDING = 'pending'
    WORKING_ON = 'working-on'
    FINISHED = 'finished'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (WORKING_ON, 'Working On'),
        (FINISHED, 'Finished'),
    ]
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)
    tests = models.ManyToManyField(Test, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    status =  models.CharField(max_length=45, choices=STATUS_CHOICES, default=PENDING)
    
    def duration_unformated(self):
        if self.start_time :
            if self.finish_time:
                duration = self.finish_time - self.start_time
            else:
                duration = timezone.now() - self.start_time
            return duration
        
        return 0 
    
    def duration(self):
        if self.start_time:
            if self.finish_time:
                duration = self.finish_time - self.start_time
            else:
                duration = timezone.now() - self.start_time

            # Convert the duration to hours and minutes
            hours = duration // timedelta(hours=1)
            minutes = (duration % timedelta(hours=1)) // timedelta(minutes=1)

            return f"{hours} hours {minutes} minutes"

        return "0 hours 0 minutes"
    
    def all_tests_confirmed(self):
        return self.tests.filter(confirmed=False).count() == 0
    
    def save(self, *args, **kwargs):
        if self.accepted and not self.start_time:
            self.start_time = timezone.now()
            self.status = self.WORKING_ON
        if self.finished and not self.finish_time:
            self.finish_time = timezone.now()
            self.status = self.FINISHED
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'analysis_request'
        
    def __str__(self):
        return f"{self.appointment.client.user.first_name} {self.appointment.client.user.last_name} - Analysis Requested #{self.id}"

    
class TestResult(models.Model):
    request = models.OneToOneField(AnalysisRequest, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True, blank=True)
    approved = models.BooleanField(default=False)

    class Meta:
        db_table = 'test_result'
        
    def __str__(self):
        return f"Test Result #{self.id}"
    
    
class Diabetes(models.Model):
    result = models.OneToOneField(TestResult, on_delete=models.CASCADE)
    positive = models.BooleanField()
    probability = models.FloatField()
    
    def __str__(self):
        return f"Diabetes Prediction #{self.result.id}: {self.probability}%"
    
class Anemia(models.Model):
    result = models.OneToOneField(TestResult, on_delete=models.CASCADE)
    positive = models.BooleanField()
    probability = models.FloatField()
    
    def __str__(self):
        return f"Anemia Prediction #{self.result.id}: {self.probability}%"
        
class Report(models.Model):
    test_result = models.OneToOneField(TestResult, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100000, null=True, blank=True)
    
    class Meta:
        db_table = 'report'
        
    def __str__(self):
        return f"Report #{self.id}"

class Invoice(models.Model):
    PRE_PAY = 'PP'
    ON_RECEIVE = 'OR'
    PAYMENT_CHOICES = [
        (PRE_PAY, 'Pre-Pay'),
        (ON_RECEIVE, 'On-Receive'),
    ]
    
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    creation_time = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE)

    class Meta:
        db_table = 'invoice'
        
    def __str__(self):
        return f"Invoice #{self.id}"
    


class Evaluation(models.Model):
    GENDER_CHOICES = [
        (0.0, 'Male'),
        (1.0, 'Female')
    ]
    
    SMOKING_CHOICES = [
        (0.0, 'Never'),
        (1.0, 'No Info'),
        (2.0, 'Former'),
        (3.0, 'Not Current'),
        (4.0, 'Ever'),
        (5.0, 'Current')
    ]

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE )
    gender = models.FloatField(choices=GENDER_CHOICES)
    age = models.FloatField()
    hypertension = models.FloatField(choices=[(0.0, 'No'), (1.0, 'Yes')])
    heart_disease = models.FloatField(choices=[(0.0, 'No'), (1.0, 'Yes')])
    smoking_history = models.FloatField(choices=SMOKING_CHOICES)
    bmi = models.FloatField()

    def __str__(self):
        return f"Evaluation #{self.id}"
    
    
class Statistics(models.Model):
    @staticmethod
    def get_most_common_tests():
        return Test.objects.values('test_offered__name').annotate(count=Count('test_offered')).order_by('-count')[:3]

    @staticmethod
    def get_most_common_tests_with_count():
        most_common_tests = Statistics.get_most_common_tests()
        return [(item['test_offered__name'], item['count']) for item in most_common_tests]

    @staticmethod
    def get_last_four_months_appointments_count():
        today = date.today()
        four_months_ago = today - timedelta(days=120)

        appointments_count = (
            Appointment.objects
            .filter(date__gte=four_months_ago)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        table = []
        for entry in appointments_count:
            month_name = entry['month'].strftime('%B')
            count = entry['count']
            table.append({'month': month_name, 'count': count})

        return table
    


    @staticmethod
    def get_total_earnings():
        total_earnings = Payment.objects.filter(payed_appointment_fee=True).aggregate(total=Sum('total_amount_payed'))['total']
        if total_earnings :
            return total_earnings 
        else : 
            return Decimal(0) 

    @staticmethod
    def get_monthly_revenue():
        average_revenue = (
            Payment.objects.filter(payed_appointment_fee=True)
            .annotate(month=TruncMonth('appointment__date'))
            .values('month')
            .annotate(total_revenue=Sum('total_amount_payed'))
            .aggregate(average=Avg('total_revenue'))['average']
        )
        if average_revenue:
            return '{:.2f}'.format(average_revenue)
        else:
            return Decimal(0)
        
    @staticmethod
    def get_client_count():
        client_count = Client.objects.all().count()
        return client_count
    
    @staticmethod
    def get_new_clients():
        # Calculate the date 7 days ago
        seven_days_ago = date.today() - timedelta(days=7)
        
        # Retrieve all users who joined in the past 7 days
        new_clients = Client.objects.filter(user__date_joined__gte=seven_days_ago).count()        
        
        return new_clients
    
    @staticmethod
    def get_total_complaints():
        total_complaints = Complaint.objects.all().count()
        return total_complaints
    
    @staticmethod
    def get_complaints_last_7_days():
        # Calculate the date 7 days ago
        seven_days_ago = date.today() - timedelta(days=7)
        
        # Retrieve the count of complaints created in the last 7 days
        complaints_last_7_days = Complaint.objects.filter(date__gte=seven_days_ago).count()
        
        return complaints_last_7_days