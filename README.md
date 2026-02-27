#  Food Redistribution System

A Flask-based web application that connects **donors**, **recipients**, **inspectors**, and **admins** to manage food redistribution efficiently.  
It enables users to donate surplus food, claim it, track deliveries, and manage approvals — promoting zero food waste.

---

##  Project Structure

```
Food_Redistribution_System/
│
├── templates/
│   ├── admin_dashboard.html
│   ├── base.html
│   ├── donation_history.html
│   ├── donor_dashboard.html
│   ├── index.html
│   ├── inspector_dashboard.html
│   ├── login.html
│   ├── manage_users.html
│   ├── my_claims.html
│   ├── recipient_dashboard.html
│   ├── register.html
│   ├── track_delivery.html
│
├── app.py               # Main Flask app
├── create_db.py         # Creates SQLite DB and tables
├── database.db          # SQLite database (auto-generated)
├── requirements.txt     # Dependencies list
├── .env                 # Environment variables (SECRET_KEY, ADMIN_SECRET_CODE)
├── .gitignore
└── README.md
```

---

##  Setup Instructions

### 1️ Clone or Download the Repository
```bash
git clone https://github.com/yourusername/FoodRedistributionSystem.git
cd FoodRedistributionSystem
```

### 2️ Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
# OR
source venv/bin/activate      # macOS/Linux
```

### 3️ Install Dependencies
```bash
pip install -r requirements.txt
```

---

##  Environment Setup

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key_here
ADMIN_SECRET_CODE=your_admin_code_here
```

>  You don’t need any DB credentials since the app uses **SQLite (`database.db`)**.

---

##  Initialize the Database

Run the following command to create the SQLite database and tables:

```bash
python create_db.py
```

 This will generate a file named `database.db` in your project root.

---

##  Run the Application

Start the Flask development server:

```bash
python app.py
```

Then open your browser and visit:

 `http://127.0.0.1:5000`

---

##  User Roles and Features

| Role | Capabilities |
|------|---------------|
| **Donor** | Register donations, view donation history, and track deliveries. |
| **Recipient** | Browse available food, claim donations, view claim status. |
| **Inspector** | Review and approve/reject claims and donations. |
| **Admin** | Manage all users, monitor donations, claims, and system activity. |

---

##  Key Routes Overview

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/register` | New user registration |
| `/login` | User login |
| `/donor_dashboard` | Donor dashboard |
| `/recipient_dashboard` | Recipient dashboard |
| `/inspector_dashboard` | Inspector verification panel |
| `/admin_dashboard` | Admin management panel |
| `/track_delivery` | Delivery tracking |
| `/my_claims` | Recipient’s claim history |
| `/manage_users` | Admin-only user management |
| `/donation_history` | Donor’s past donations |

---

##  How It Works

1. **Donors** register surplus food donations.  
2. **Recipients** request or claim available donations.  
3. **Inspectors** review pending claims and click **Approve** or **Reject**.  
4. **Admins** can monitor the entire system and manage user accounts.  
5. Delivery progress can be tracked via the **Track Delivery** section.

---

##  Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS (Inline in templates)
- **Database:** SQLite
- **Auth & Security:** Flask sessions, password hashing (`werkzeug.security`)
- **Environment Management:** `python-dotenv`

---

##  Requirements File

```
Flask
python-dotenv
Werkzeug
```

> (If you used SQLite, `mysql-connector-python` is **not needed**.)

---

##  Development Notes

- Run only in **debug mode** for development.  
- SQLite is sufficient for local or small-scale deployment.  
- For large production use, migrate to MySQL or PostgreSQL easily later.  
- Keep `.env` and `database.db` out of GitHub (already in `.gitignore`).  

---

##  Future Improvements

- Email alerts for approvals/rejections.  
- OTP-based user verification.  
- Real-time delivery tracking (Socket.IO).  
- Integration with Google Maps API for pickup/drop visualization.  

---

##  Quick Run Recap

```bash
 git clone https://github.com/Kunal-t20/food_delivery_system-f1-.git

 cd FoodRedistributionSystem (or cd file path)

- create virtual env:

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python create_db.py
python app.py
```

Then visit **http://127.0.0.1:5000** 
