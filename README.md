# Drugstoc Inventory Management APIs Assessment

A simple Django backend for a inventory mananagement that manages users, products, orders and reports. It supports basic CRUD (Create, Read, Update, Delete) operations for all services.

## Features

- Endpoints for managing users authentication and authorization with RBAC
- Endpoints for products where only admin can make full CRUD operations
- Basic error handling
- Normal users can create orders with list of products
- Reporting endpoints for sales and products stock management


## SQL Database Design

    [SQLDesign](https://drawsql.app/teams/peaknews/diagrams/drugstoc-inventory)

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

4. **Run and Execute Tests Script**

    ```
        chmod +x run_tests.sh # Make it executable script
        ./run_tests.sh
    ```

5. **Start Server**

    ```bash
        make runserver
    ```
6. **Create Super User**

    ```bash
        make createsuperuser
    ```

## Internal API Endpoints Documentation

    ```
        ./api_doc.txt file
    ```