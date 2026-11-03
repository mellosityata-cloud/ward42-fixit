# ward42-fixit
Ward 42 Fix-It

Ward 42 Fix-It is a web application developed for the Mamelodi East Residents’ Association in Ward 42, Tshwane. It allows residents to report community faults, receive reference numbers and check the progress of submitted reports. Coordinators can log in to view reports, manage submissions and update their statuses.

Features

* Submit community fault reports.
* Select a fault category and provide location details.
* Upload an optional photograph as supporting evidence.
* Receive a unique reference number.
* Check the status of submitted reports.
* Coordinator login and report management.
* Update report statuses to Open, In Progress or Closed.
* Responsive interface for mobile and desktop devices.
* Progressive Web App (PWA) functionality.

Installation and Setup

1. Clone or download the repository.
2. Activate the virtual environment:

source source/venv/bin/activate

3. Install the required dependencies:

pip install -r requirements.txt

4. Start the Flask application:

flask --app app run

5. Open the application in your browser:

http://127.0.0.1:5000

Test Coordinator Login

Use the following demonstration credentials to access the coordinator dashboard:

* Username: coordinator
* Password: Ward42Test!

Technologies Used

* Python
* Flask
* SQLite
* HTML
* CSS
* JavaScript
* Bootstrap
* Service Workers and Web App Manifest

Project Purpose

The application aims to improve communication between residents and local coordinators by providing a simple digital platform for reporting and tracking community faults.
