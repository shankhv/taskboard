# 🧩 TaskBoard API

A modular FastAPI-based TaskBoard application built for the BabyBillion developer assignment.  
It manages **tasks, categories, and tags** with relationships using **MongoDB**, **Punq (DI)**, and **Motor** for async I/O.

---

## 🚀 Tech Stack
- **FastAPI** (async web framework)
- **Motor** (async MongoDB driver)
- **Punq** (dependency injection)
- **Pydantic v2** (validation & serialization)
- **Python 3.10+**

---

## 📁 Project Structure
app/
├── entities/ # Domain models
├── repositories/ # MongoDB data access logic
├── use_cases/ # Business logic
├── controllers/ # FastAPI route handlers
├── schemas/ # Request/response validation models
├── database.py # MongoDB connection (Motor)
├── container.py # Punq dependency container
└── main.py # App entry point

```bash
# 1. Install dependencies
pip install -r requirements.txt
```
