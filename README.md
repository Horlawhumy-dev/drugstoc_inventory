# Drugstoc Inventory Management APIs Assessment

A simple Django backend for a inventory mananagement that manages users, products, orders and reports. It supports basic CRUD (Create, Read, Update, Delete) operations for all services.

## Features

- Endpoints for managing users authentication and authorization with RBAC
- Endpoints for products where only admin can make full CRUD operations
- Basic error handling
- Normal can create orders with list of products
- Reporting endpoints for sales and products stock management

## Project Structure

drugstoc_inventory/
│ ├── init.py
│ ├── main.py
│ ├── crud/
│ │ ├── init.py
│ │ ├── author.py
│ │ └── post.py
│ ├── models/
│ │ ├── init.py
│ │ ├── author.py
│ │ └── post.py
│ ├── schemas/
│ │ ├── init.py
│ │ ├── author.py
│ │ └── post.py
│ ├── db/
│ │ ├── init.py
│ │ └── database.py
│ └── api/
│ ├── init.py
│ ├── author.py
│ └── post.py
└── README.md
└── run_tests.sh
└── requirements.txt


## Getting Started

### Prerequisites

- Python 3.7+ install
- Make install

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Horlawhyumy-dev/drugstoc_inventory.git
   cd drugstoc_inventory


2.  **Create Virtual Environment and Install Requirements**
    ```bash
        python3 -m venv env
        source env/bin/activate  # On Windows use `env\Scripts\activate`
        make install
    ```

3. **Run Migrations**
    ```bash
        make migrate
    ```

4. **Run and Excute Tests Script**

    ```
        chmod +x run_tests.sh
        ./run_tests.sh
    ```

5. **Start Server**

    ```bash
        make runserver
    ```

## Internal API Endpoints Documentation

    ```
        ./api_doc.txt file
    ```