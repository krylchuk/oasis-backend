### Gardening Services Backend API

This project is a **Python-based backend** built with **Flask**, designed to provide API endpoints for a gardening services website. The backend manages all interactions between the frontend and the **MySQL database**, allowing efficient handling of customer requests, service management, and other essential functionalities.

#### Key Features:
- **Flask Framework**: A lightweight and flexible framework for building RESTful APIs, ensuring fast development and easy scalability.
- **MySQL Integration**: The backend is connected to a MySQL database that stores all relevant data, such as customer information, services, bookings, and transactions.
- **CRUD Operations**: Provides full Create, Read, Update, and Delete (CRUD) functionalities for managing gardening services and customer data through secure API endpoints.
- **User Authentication**: Implements basic authentication and authorization mechanisms to secure API access, ensuring that sensitive data is protected.
- **Service Management**: Endpoints allow the addition, modification, and deletion of various gardening services, such as lawn mowing, tree pruning, garden maintenance, and more.
- **Customer Interaction**: Facilitates customer requests for quotes, booking of services, and tracking the status of their requests.
- **CORS Enabled**: Uses `Flask-CORS` to handle cross-origin requests, making it easy to integrate with a variety of frontend frameworks, including React and Next.js.
- **Environment Configuration**: Secure handling of database credentials and API keys using `.env` files and `python-dotenv`.

#### Technologies Used:
- **Flask**: For building the API and handling HTTP requests.
- **MySQL**: As the relational database for storing and managing service data.
- **Flask-MySQLdb**: A Flask extension to interact with the MySQL database.
- **bcrypt**: For secure password hashing.
- **Requests**: For making HTTP requests to external services.

This backend is designed to seamlessly integrate with a React or Next.js frontend, offering a reliable and scalable solution for managing gardening services and customer interactions.
