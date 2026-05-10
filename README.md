# Laboratory Information System (LIS)

## 1. PROJECT OVERVIEW
This Laboratory Information System (LIS) is an enterprise-grade web application built to manage clinical lab workflows securely and efficiently. It tracks the complete lifecycle of lab orders, encompassing patient registration, assay selection, sample collection, and result reporting.

**Workflow Lifecycle:**
`Ordered` → `Collected` → `In-Lab` → `Completed`

**Tech Stack:**
- **Backend**: Django, Python, SQLite (configurable for PostgreSQL)
- **API Engine**: Django REST Framework (DRF)
- **Authentication**: SimpleJWT (JSON Web Tokens)
- **Frontend UI**: Django Templates, Bootstrap 5, GSAP Animations

---

## 2. FEATURES
- **Role-Based Access Control (RBAC)**: Secure access mapped strictly to clinical roles.
- **Patient Registration**: Capture MRN, demographics, and contact info with strict DOB validation.
- **Lab Order Workflow**: Multi-assay order cart with dynamic pricing.
- **Sample Collection**: Phlebotomist worklist to securely record sample IDs and condition.
- **Result Entry**: Lab Technician desk with specific value entry, normal range tracking, and high/low/critical flagging per assay.
- **Clinical Reports**: Consolidated, printable final patient reports.
- **REST APIs**: Full headless operation capabilities via `/api/v1/`.
- **JWT Authentication**: Token-based security securing all API endpoints.
- **Print/PDF Reporting**: Native browser print optimization for final lab reports.
- **Dashboard Analytics**: Real-time stats counting orders, patients, and pending lab work.

---

## 3. PROJECT STRUCTURE
The project is modularized into distinct Django apps:
- **`accounts`**: Custom User model enforcing distinct clinical roles.
- **`patients`**: Patient demographics, strict MRN, and DOB validation constraints.
- **`labtests`**: The core assay menu, test categories, pricing, and turnaround definitions.
- **`orders`**: Transactional models bridging Patients, Physicians, and selected assays (`OrderLine`).
- **`results`**: Final clinical values, flags, and remarks tied back to specific assays.

---

## 4. INSTALLATION STEPS

```bash
# Clone the repository
git clone <repository-url>
cd project

# Create a virtual environment
python -m venv env

# Activate the virtual environment
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 5. DATABASE SETUP

```bash
# Apply migrations to build the database schema
python manage.py migrate

# Create a superuser (optional, for direct Django Admin access)
python manage.py createsuperuser

# Launch the development server
python manage.py runserver
```

---

## 6. TEST CREDENTIALS

Use the following pre-configured credentials to evaluate the role-based UI and API limitations:

| Role | Username | Password |
| :--- | :--- | :--- |
| **ADMIN** | `admin` | `admin123` |
| **NURSE** | `nurse1` | `abcd@1234` |
| **PHLEBOTOMIST** | `phlebo1` | `abcd@1234` |
| **PHYSICIAN** | `physician1` | `abcd@1234` |
| **LAB TECHNICIAN** | `tech1` | `abcd@1234` |

---

## 7. API DOCUMENTATION

Base URL: `http://127.0.0.1:8000/api/v1/`

### Auth Endpoints
- `POST /auth/token/`: Obtain JWT Access and Refresh Tokens
- `POST /auth/token/refresh/`: Refresh an expired Access Token
- `POST /auth/login/`: Alias for login token acquisition
- `POST /auth/logout/`: Destroy token session (Client side + Stateless)

### Patient Endpoints
- `GET /patients/`: List patients
- `POST /patients/`: Register a new patient

### Order & Workflow Endpoints
- `GET /orders/`: List all orders
- `POST /orders/`: Create a new multi-assay order
- `PATCH /orders/{id}/collect/`: Progress order from `Ordered` (1) to `Collected` (2)
- `PATCH /orders/{id}/receive/`: Progress order from `Collected` (2) to `In-Lab` (3)

### Result Endpoints
- `POST /orders/{id}/results/`: Push result values into an `In-Lab` order, progressing to `Completed` (4)
- `GET /orders/{id}/report/`: Fetch a finalized clinical report

---

## 8. WORKFLOW DESCRIPTION

The system utilizes a strict forward-only status progression:
**`Ordered (1)` → `Collected (2)` → `In-Lab (3)` → `Completed (4)`**

**Role Ownership:**
1. **Physician** creates an order (`Ordered`).
2. **Phlebotomist** draws blood and records sample ID/condition (`Collected`).
3. **Lab Technician** receives the physical sample in the lab (`In-Lab`).
4. **Lab Technician** inputs assay results, flags, and remarks (`Completed`).

---

## 9. SCREENSHOTS SECTION
Visual walkthroughs of the LIS interface can be found in the `/screenshots/` directory within this repository.

---

## 10. ERD SECTION
For a complete architectural view of the database entities, relationships, and foreign key constraints, refer to `ERD.png` located in the repository root.