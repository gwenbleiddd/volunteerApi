# Volunteer Management API

## 📌 Overview

The Volunteer Management API is a backend system designed to connect volunteers with community service opportunities in their local area. Organisations can post opportunities, while volunteers can search, apply, and track their participation.

The system supports user roles, authentication, opportunity management, and application tracking.

---


## ⚙️ Features

### 👤 User Management
- Volunteer registration with skills, availability, and location
- Organisation registration with mission details and contact information
- Role-based access control (volunteer / organisation)
- JWT-based authentication
- User profile updates

---

### 🏢 Opportunity Management (Organisations)
- Create volunteer opportunities
- Update and delete opportunities
- View applicants for each opportunity
- Opportunity includes:
  - Title
  - Description
  - Required skills
  - Location
  - Start and end dates

---

### 🔍 Search & Apply (Volunteers)
- Search opportunities by:
  - Location
  - Required skills
  - Date range
- Apply to opportunities
- Track application status:
  - Pending
  - Accepted
  - Rejected

---

### 🔔 Notifications 
- Notify organisations when volunteers apply
- Notify volunteers when application status changes

---

### ⏱️ Tracking & Feedback 
- Track hours spent per opportunity
- Organisations can provide feedback after completion

---

## 🛠️ Tech Stack

- Backend: Django / Django REST Framework
- Authentication: SimpleJWT
- Database: SQLite
- API Testing: Postman
- Documentation: Swagger / OpenAPI

---

## 📂 Project Structure

```
volunteer_api/
│── users/
│── opportunities/
│── applications/
│── notifications/
│── settings.py
│── urls.py
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/volunteer-api.git
cd volunteer-api
```

---

### 2. Create virtual environment
```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

---

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

### 4. Run migrations
```bash
python manage.py migrate
```

---

### 5. Start the server
```bash
python manage.py runserver
```

---

## 🔑 Authentication

This API uses JWT authentication.

### Obtain token
```http
POST /api/token/
```

### Use token in requests
```http
Authorization: Bearer <your_token>
```

---

## 📡 Example Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/register | Register user |
| POST | /api/login | Login user |
| GET | /api/opportunities | List opportunities |
| POST | /api/opportunities | Create opportunity |
| POST | /api/apply | Apply to opportunity |

---

## 📬 Example: Create Opportunity

### Request
```json
{
  "title": "Beach Clean-Up Volunteer",
  "description": "Help clean the local coastline",
  "required_skills": "Teamwork",
  "location": "Siparia",
  "start_date": "2024-06-01",
  "end_date": "2024-06-02"
}
```

### Response
```json
{
  "message": "Opportunity created successfully",
  "id": 1
}
```

---

## 🧠 System Design

The system is structured into modular applications:

- Users: authentication and profiles
- Opportunities: volunteer postings
- Applications: application handling and status tracking
- Notifications: status updates

This separation improves scalability and maintainability.

---

## 🧪 Testing

- API tested using Postman
- Unit tests included for models, serializers, and views (if applicable)

---


## 📄 License

This project is developed for academic purposes as part of **ITEC 443**.

---

## 👤 Author

Dominic Salandy  
Final-year BSc Information Technology Student  
GitHub: https://github.com/gwenbleiddd

---
