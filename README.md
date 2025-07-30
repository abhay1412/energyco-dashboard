# EnergyCo Operations Dashboard

An interactive, role-based web dashboard for monitoring and managing energy station operations. Built with Django and Django Rest Framework, this application provides real-time data visualization and secure user management.

![Dashboard Screenshot](https://i.imgur.com/3e4b3f.png)

## Key Features

* **Role-Based Access Control:** Four distinct user roles (Admin, Country Lead, Station Manager, Viewer) with tailored permissions and data visibility.
* **Interactive Data Visualization:** Real-time charts powered by Chart.js display key performance indicators like power output, efficiency, and temperature across different countries and stations.
* **Comprehensive User Management:** Admins can create, edit, and delete users through a secure, modal-based interface.
* **Hierarchical Data Filtering:** Users only see data for the stations and countries they are assigned to, ensuring data security and relevance.
* **Audit Trail:** A complete log of all significant user actions (creations, updates, deletions) for accountability and tracking.
* **RESTful API:** A well-structured API built with Django Rest Framework serves all data to the frontend.

## Tech Stack

* **Backend:** Django, Django Rest Framework
* **Database:** PostgreSQL
* **Frontend:** HTML, Tailwind CSS, Chart.js
* **Authentication:** Django's built-in user authentication system

## Setup and Local Installation

Follow these steps to get the project running on your local machine.

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/energyco-dashboard.git
cd energyco-dashboard
```

#### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
Install all required packages from the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

#### 4. Database Setup
This project uses PostgreSQL. Ensure you have it installed and running.
- Create a new database.
- Update the `DATABASES` setting in `energy_project/settings.py` with your database credentials.

#### 5. Run Database Migrations
Apply the database schema to your newly created database.
```bash
python manage.py migrate
```

#### 6. Load Initial Data
The project includes a custom management command to populate the database with sample data.
```bash
python manage.py load_data
```
This will create countries, regions, stations, users, and metrics. The default password for all created users is `password123`.

#### 7. Run the Development Server
```bash
python manage.py runserver
```
The application will be available at `http://127.0.0.1:8000/`.

## API Endpoints

The core API endpoints are available under the `/api/` route:

| Endpoint              | Methods         | Description                                     |
| --------------------- | --------------- | ----------------------------------------------- |
| `/api/users/`         | `GET`, `POST`   | List all users or create a new one.             |
| `/api/users/<id>/`    | `GET`, `PUT`, `DELETE` | Retrieve, update, or delete a specific user.    |
| `/api/users/me/`      | `GET`           | Get the profile of the currently logged-in user.|
| `/api/stations/`      | `GET`           | List all stations visible to the current user.  |
| `/api/countries/`     | `GET`           | List all countries visible to the current user. |
| `/api/metrics/`       | `GET`           | List all performance metrics.                   |
| `/api/auditlog/`      | `GET`           | List all audit log entries (Admins only).       |
