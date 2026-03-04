# Django E-Commerce Store
## Overview

This is a Django-based e-commerce web application that allows users to:

- Browse products

- Add items to a shopping cart

- Make payments online

The application features a responsive interface and integrates M-Pesa STK Push for mobile payments, making it ideal for businesses in East Africa.

## Key Features

- #### User authentication: Registration, login, and logout

- #### Product browsing: Categories, search, and detailed product pages

- #### Shopping cart: Add, remove, and update items

- #### Checkout system: Complete orders and payments

- #### Admin dashboard: Manage products, orders, and users

- #### Mobile payment integration: M-Pesa STK Push

- #### Responsive design: Works on desktop and mobile

- #### Modern styling: Styled with CSS for a polished look

## Technologies Used

- #### Backend: Python, Django

- #### Frontend: HTML, CSS, JavaScript

- #### Database: SQLite (development) / MySQL (production)

- #### Payment Integration: Safaricom Daraja API (M-Pesa STK Push)

- #### Tools: Visual Studio Code, Git

## Getting Started
### Prerequisites

Make sure you have installed:

- Python 3.x

- pip (Python package installer)

- Git

### Installation

#### 1. Clone the repository

- git clone https://github.com/priscamuli/josmayawebsite
- cd ecommerce_site

#### 2. Create a virtual environment

- python -m venv env

#### 3. Activate the virtual environment

- ##### Windows:

- env\Scripts\activate

- ##### macOS/Linux:

- source env/bin/activate

#### 4. Install dependencies

- pip install -r requirements.txt

#### 5. Apply database migrations

- python manage.py migrate

#### 6. Create a superuser for admin access

- python manage.py createsuperuser

#### 7. Run the development server

- python manage.py runserver

###### Open your browser and visit http://127.0.0.1:8000/ to view the project.

### Usage

- Browse products and add items to your cart

- Proceed to checkout and complete payment using M-Pesa STK Push

- Admin users can manage products, orders, and users via the Django admin panel

### Project Structure
django-ecommerce/
├── ecommerce/          # Project settings
├── store/              # Main app (products, cart, orders)
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── media/              # Uploaded images
├── manage.py           # Django management script
├── requirements.txt    # Dependencies
└── README.md           # Project documentation

### License

This project is licensed under the MIT License. See the LICENSE
 file for details.
