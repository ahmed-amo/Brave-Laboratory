# Brave Lab

Welcome to Brave Lab! We are a blood laboratory that provides convenient and efficient services. We provide the option to book appointments online, while also having fast online payment integrations with PayPal. The results of our tests are accurate and are powered by Modern AI Technologies. Our mission is to deliver clean and timely results while utilizing advanced AI models for disease predictions, such as anemia and diabetes.

## Features

- **Appointment Booking**: Easily schedule appointments online.
- **Fast Online Payments**: Secure and hassle-free payment options, including PayPal integration.
- **Real-time Result Tracking**: Clients can track the progress of their test results in real-time.
- **Complaint System**: A built-in system for handling complaints, which automatically sends emails to relevant parties for resolution.
- **Accurate Results**: Trustworthy and precise blood test results.
- **Disease Predictions**: AI-powered models for predicting diseases like anemia and diabetes.
- **Simple Interface**: A user-friendly interface for managing all steps of testing and appointment management.
- **Profile Settings**: A basic interface for users to manage their profile settings, such as profile picture, email, and password.
- **Chat System**: Real-time communication between nurses and the chief medical supervisor (auditor) using AJAX for seamless interaction.
- **Search, Filter, and Sort**: Enhanced functionality to search, filter, and sort various lists within the application.
- **Nurse Account**: A dedicated account for nurses to manage clients in the lobby and input test results.
- **Receptionist Account**: An account for receptionists to handle appointment booking, client account creation, and payment and invoice management.
- **Auditor Account**: An account for the chief medical supervisor to access various statistics of the company, approve and sign test results, and handle complaints.
- **Admin Account**: An account with privileges for performing basic CRUD (Create, Read, Update, Delete) operations.

## Collaborators

- [Farouk Rahal](https://github.com/FaroukRahal)
- [Ahmed Amoukrane](https://github.com/zMARTVAL)

## Technologies Used

- Frontend: HTML, CSS, JavaScript, Bootstrap
- Backend: Django
- Database: SQLite3
- AI/ML: Logistic Regression algorithms for anemia and diabetes prediction

# Getting Started

## **Local Setup**
To get started with Brave Lab, follow these steps:
1. Clone the repository:
```
git clone https://github.com/AdemBendjama/Brave-Lab.git
cd Brave-Lab
```
2. Install the required dependencies: 
```
pip install -r requirements.txt
```
3. Run the application using 
```
python manage.py runserver 
```
or
```
py manage.py runserver
```
4. Visit `http://localhost:8000` in your browser to access Brave Lab.

> **Note**: In the local version, email functionality depends on settings.py credentials.

## Screenshots

### Homepage

![Homepage](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/e5d727dd-29fe-40a2-805c-f4246873466a)

### Manage Profile

![Profile](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/48dd309e-1689-41a7-91db-9465801328bf)

### Client Book Appointment

![Book](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/e65048ed-f514-43ca-a6d7-81f2da787b17)

### Client Test Results

![CResults](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/77d36fef-352f-414d-9571-2ed6b150e01e)

### Client Online Payment With PayPal

![Paypal01](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/0353e6d0-b8fe-4171-8ef9-ec708a7fb4b7)

### Nurse Fill Test Values

![FillTest](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/0825bc41-d77c-4c11-b610-089319d7b29b)

### Nurse Chat

![NChat](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/15f6dc58-acef-4587-ac14-eff5cf6a9e44)

###  Auditor Chat Rooms

![ChatRooms](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/c6934054-a6d0-498b-a458-4be6bccbcb26)

###  Auditor Chat

![AChat](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/8430b544-ecae-4889-b39d-eb8786718686)

### Auditor Stats

![Stats](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/02507b00-6466-4443-89f4-95757e205b9c)

### Admin Interface

![Admin](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/43107cee-69f6-47cb-9d38-727405b35a10)

### Invoice

![InvoicePDF](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/2c0b6f10-e0dc-4337-bb98-d42f4ef95b58)

### Test Results and AI Prediction

![ResultsPDF](https://github.com/AdemBendjama/Brave-Lab/assets/93732841/c119f76f-a1c9-488f-9464-83492ec1914c)

## Future Work

Here are the several areas i could work on to improve the site's functionality, security and Code readability:

- Hosting the website with Https and SSLTLS and a custom domain. &#x2714;
- Changing the current database Sqlite3 into a more secure and robust database management system like PostgreSQL or MySQL. &#x2714;
- Enhancing the security of the payment integration with PayPal to ensure the safety of user transactions.
- Adding Cloud Storage for image uploads
- Investigating the possibility of integrating face recognition and OCR (Optical Character Recognition) AI models for advanced functionality.
- Conducting code reviews and optimizing the codebase to improve efficiency and maintainability.
- Adding comprehensive documentation to guide users and developers in understanding the system.
- Organizing files and folders to enhance the project's structure and maintain a clean codebase.
- Adding more styles and visual enhancements to improve the overall user experience.

We are committed to continuously improving Brave Lab and providing an exceptional user experience. Stay tuned for updates and new features!

## Contact

If you have any questions or inquiries, feel free to contact me at amokrane.ahmed10@gmail.com
