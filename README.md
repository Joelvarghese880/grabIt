# 🏠🚗 GrabIt – Property & Vehicle Rental Platform

**GrabIt** is a full-stack web application built with **Python Django** that allows users to rent **properties and vehicles** seamlessly.  
It provides a modern classified-listing experience similar to **OLX**, **99acres**, and **Revv Cars**, featuring real-time chat, booking management, and secure payments.

---

## 🚀 Features

### 👤 User Management
- User registration, login, and profile management  
- Extended `UserProfile` model for user-specific data  
- Dashboard to manage listings, bookings, and payments  

### 🏡 Listings
- Add, update, or delete property and vehicle rental listings  
- Image uploads and category-based filtering  
- Search and filter functionality  

### 📅 Bookings
- Rent properties or vehicles for selected dates  
- Booking status: `Pending`, `Confirmed`, `Canceled`  
- Owners can approve or cancel bookings  
- Users can cancel their own bookings  

### 💬 Real-time Chat
- Live chat between customers and owners using **Django Channels**  
- Messages stored in the database  

### 💳 Payments
- Integrated **Cashfree** payment gateway  
- Pay securely once booking is confirmed  

### ✉️ Notifications
- Email notifications for booking confirmations and cancellations  

---

## 🧩 Tech Stack

| Category | Technology |
|-----------|-------------|
| **Backend** | Django, Django REST Framework |
| **Frontend** | HTML, CSS, JavaScript (ClassiX Template Integration) |
| **Database** | PostgreSQL |
| **Authentication** | Django Auth + Custom UserProfile |
| **Real-Time** | Django Channels, WebSockets |



---
