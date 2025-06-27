# N'Travlio - Smart Travel Agency System
## 🚀 Solution Overview

### N'Travlio is a full-stack travel package management system that enables:

  - User roles: Admin, Manager, Seller, and Customer accounts

  - Package management: Create, view, update travel packages

  - Reservations: Booking system with payment integration

  - Quotations: Automatic price calculation

  - Dashboard: Statistics and reporting for admins

### The system uses token-based authentication and provides RESTful APIs for all operations.
## 💻 Technologies Used
### Backend

  - Python 3.9+

  - Django 4.0+

  - Django REST Framework

  - SQLite (Development)

  - JWT Authentication

### Frontend

  - HTML5, CSS3, JavaScript

  - Bootstrap 5

  - jQuery (AJAX requests)

  - Font Awesome (Icons)

## 🛠️ Installation Guide
1. Clone the Repository

        git clone https://github.com/akrambengueddoudj/travel-agency.git
        cd travel-agency

2. Set Up Virtual Environment

        python -m venv venv
        source venv/bin/activate   # Linux/Mac
        venv\Scripts\activate      # Windows

3. Install Dependencies

        pip install -r requirements.txt

4. Database Setup

        # Create database file
        touch db.sqlite3
        
        # Run migrations
        python manage.py migrate

5. Create Superuser (Admin)

        python manage.py createsuperuser

6. Run Development Server

        python manage.py runserver

## 🌐 Accessing the Application

  - Frontend: http://localhost:8000/app/

  - Admin Panel: http://localhost:8000/app/admin/dashboard/

  - API Documentation: http://localhost:8000/api/swagger (if using DRF Spectacular)

## 🔑 Default Roles & Permissions

  - Admin: Full access (create via superuser)

  - Manager: Can manage packages and view reports

  - Seller: Can create reservations

  - Customer: Can browse and book packages

## 📂 Project Structure

N-Travlio/
├── api/             # Django app for API endpoints
├── static/          # CSS, JS, images
├── templates/       # HTML templates
├── manage.py
├── requirements.txt # Python dependencies
└── README.md

## ⚙️ Environment Configuration

### Create a .env file in project root with:

    GUIDDINI_APP_KEY=APP-APPKEYFROMGUIDDINI
    GUIDDINI_SECRET_KEY=SEC-SECRETKEYFROMGUIDDINI

## 🚨 Important Notes

  - For production, switch to PostgreSQL/MySQL

  - Configure proper CORS settings if using separate frontend

  - Payment integration requires additional merchant account setup

  - Email functionality needs SMTP configuration

## 🤝 Contributing

  - Fork the repository

  - Create your feature branch (git checkout -b feature/AmazingFeature)

  - Commit your changes (git commit -m 'Add some AmazingFeature')

  - Push to the branch (git push origin feature/AmazingFeature)

  - Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
## ✉️ Contact

For support, email: support@ntravlio.com

# Happy travels with N'Travlio! ✈️🌍
