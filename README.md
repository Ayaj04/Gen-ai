# FastAPIGuide

## Product
FastAPIGuide is a beginner-friendly project that helps students understand FastAPI and the basics of building APIs using Python.

## User
Python beginners, college students, and aspiring backend developers.

## Problem
Beginners may find it difficult to understand API concepts, endpoints, HTTP requests, and responses. FastAPIGuide aims to make these concepts easier to learn through simple explanations and examples.

## Data Source
Official FastAPI documentation: https://fastapi.tiangolo.com/

The project may also use sample questions, example inputs, and demonstration API responses for learning purposes.

## Project Files
- day01_intro.py — Displays the project information and interacts with the user.
- day01_menu.py — Provides an interactive learning menu.


## How to run

### 1. Create and activate a virtual environment

Windows PowerShell:

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1

### 2. Install dependencies

    python -m pip install -r requirements.txt

### 3. Run the API

    python -m uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs

### 4. Available endpoints

- GET /health
- GET /records?limit=5
- GET /records/{id}
- GET /search?q=HTTPException
- POST /questions

### 5. Explore documentation data

    python -m analysis.explore

### 6. Search method

Smart Search uses TF-IDF and cosine similarity to
rank FastAPI documentation records.

Data source: https://fastapi.tiangolo.com/tutorial/
