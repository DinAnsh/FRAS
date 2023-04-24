# FRAS - Face Recognition-based Attendance System
FRAS is a face recognition-based attendance system developed using Python and Django. The system provides a convenient, accurate, and secure way to track attendance in various organizations, schools, and universities.

## Setup
To set up the FRAS application, follow the steps below:

- Clone the repository to your local machine.
- Install [Python](https://www.python.org/downloads/)=3.7.0 or [Anaconda](https://www.anaconda.com/products/distribution).
- Create a virtual environment using the following command:
  - **`python3 -m venv .venv`**
  - This will create a virtual environment with the name **'.venv.'**
  - If you are using Windows, use the following command:
  - **`python -m venv .venv`**
- Activate the virtual environment using the following command:
  - **`source .venv/bin/activate`**
  - For Windows users, use the following command:
  - **`.venv\Scripts\activate.bat`**
- Install the required dependencies by running the following command:
  - **`pip install -r requirements.txt`**
- Set up the database by running the following command:
  - **`python manage.py migrate`**

## Backend Framework
FRAS is built on **Django**, a popular open-source Python web framework that follows the Model-View-Template (MVT) architecture. Django provides a high-level, efficient, and secure way to develop web applications. The framework comes with a built-in administrative interface, robust security features, and a wide range of tools and libraries for rapid development.
<img src="https://user-images.githubusercontent.com/60287228/230828178-4297c75b-cd62-4461-8806-d73a8eedb231.png" alt="Django logo" width="300">

## Database
FRAS uses **SQLite** database locally with Django. SQLite is a popular relational database management system that is lightweight, fast, and reliable.
<img src="https://user-images.githubusercontent.com/60287228/230828466-449d335d-b435-4526-bfe9-63376806a1b5.png" alt="SQLite logo" width="300" >


## Ready to Run
To run the FRAS application, make sure you are in the **'/testsite'** directory, which has the **'manage.py'** file. Then, type the following command in the terminal:

**`python manage.py runserver`**

This will start the Django development server, and the application will be accessible at [this link](http://127.0.0.1:8000/).

## Pages
FRAS has several pages that allow users to perform various tasks. These pages include:

- Home
  - The home page provides a brief overview of the FRAS application and its features.

- Dashboard
  - The dashboard page displays the attendance statistics for a particular organization, school, or university. Users can view the total number of students or employees, the number of absentees, and the percentage of attendance.

- Student
  - The student page displays the list of students enrolled in a particular course or class. Users can view the student's name, photograph, and attendance status.

- Teacher
  - The teacher page displays the list of teachers or instructors assigned to a particular course or class. Users can view the teacher's name, photograph, and attendance status.

- Schedule
  - The schedule page displays the class schedule for a particular course or class. Users can view the class timing, instructor's name, and attendance status.

- Camera
  - The camera page provides a live video stream from the camera attached to the FRAS system. The video stream is used to capture images of the students or employees for attendance tracking.

## Thanks
The FRAS application was developed by [Dipendra Singh](https://github.com/dipendrasingh100), [Dinansh Bhardwaj](https://github.com/DinAnsh), [Diya Goyal](), and [Aditi Singh](https://github.com/aditisingh0409). We hope that this application will be useful to various organizations, schools, and universities in tracking attendance accurately and securely.
