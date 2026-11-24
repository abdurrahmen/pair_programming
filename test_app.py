"""Automated test suite for Lab 2 using pytest and Flask test_client."""

import pytest
from app import app
from data import BOOKS, STUDENTS


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Exercise 3 Tests: 201 Created, 400 Bad Request, 405 Method Not Allowed
# ---------------------------------------------------------------------------
def test_student_registration_success(client):
    """Test successful student registration returns 201 and student data."""
    unique_email = f"student_{len(STUDENTS) + 1}@univ.dz"
    response = client.post(
        "/students",
        data={
            "first_name": "Karim",
            "last_name": "Brahimi",
            "email": unique_email,
            "level": "M2",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["first_name"] == "Karim"
    assert data["last_name"] == "Brahimi"
    assert data["email"] == unique_email
    assert data["level"] == "M2"
    assert "id" in data


def test_student_registration_validation_errors(client):
    """Test registration failure returns 400 and full list of errors."""
    response = client.post(
        "/students",
        data={
            "first_name": "Sara",
            "email": "invalid_email_without_at",
            "level": "L4",  # Invalid level
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data
    errors = data["errors"]
    assert "last_name is required" in errors
    assert "invalid email" in errors
    assert "level must be L1, L2, L3, M1 or M2" in errors


def test_students_method_not_allowed(client):
    """Test disallowed methods return 405 Method Not Allowed."""
    response = client.put("/students")
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# Exercise 1 Tests
# ---------------------------------------------------------------------------
def test_greet(client):
    response = client.get("/greet/amina")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Hello, Amina!"


def test_square(client):
    response = client.get("/square/7")
    assert response.status_code == 200
    assert response.get_json() == {"n": 7, "square": 49}


def test_calc_success(client):
    response = client.get("/calc/add/2.0/3.0")
    assert response.status_code == 200
    assert response.get_json() == {"op": "add", "a": 2.0, "b": 3.0, "result": 5.0}


def test_calc_division_by_zero(client):
    response = client.get("/calc/div/10.0/0.0")
    assert response.status_code == 400
    assert response.get_json() == {"error": "division by zero"}


def test_calc_unknown_operation(client):
    response = client.get("/calc/mod/10.0/2.0")
    assert response.status_code == 400
    assert response.get_json() == {"error": "unknown operation"}


def test_files_path(client):
    response = client.get("/files/docs/2026/report.pdf")
    assert response.status_code == 200
    assert response.get_json() == {"parts": ["docs", "2026", "report.pdf"]}


# ---------------------------------------------------------------------------
# Exercise 2 Tests: Books API & Pagination
# ---------------------------------------------------------------------------
def test_api_books_pagination_and_filter(client):
    response = client.get("/api/books?min_year=2017&sort=price&order=desc&size=2")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 4
    assert data["page"] == 1
    assert data["size"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["price"] >= data["results"][1]["price"]


def test_api_books_invalid_sort(client):
    response = client.get("/api/books?sort=invalid_field")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_api_book_detail_and_404(client):
    response = client.get("/api/books/1")
    assert response.status_code == 200
    assert response.get_json()["id"] == 1

    response_404 = client.get("/api/books/999")
    assert response_404.status_code == 404
    assert response_404.get_json() == {"error": "book not found"}


# ---------------------------------------------------------------------------
# Exercise 4, 5, 6 HTML Pages Tests
# ---------------------------------------------------------------------------
def test_dashboard_page(client):
    response = client.get("/")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Department Dashboard" in text
    assert "Students" in text


def test_books_page(client):
    response = client.get("/books")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Book Catalogue" in text
    assert "Fluent Python" in text


def test_profile_page_and_initials(client):
    response = client.get("/profile/1")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Yacine" in text
    assert "HADDAD" in text
    assert "Y.H." in text  # Test bonus initials filter
    assert "Graduating this year" in text  # Yacine is L3


def test_profile_not_found(client):
    response = client.get("/profile/999")
    assert response.status_code == 404
    text = response.get_data(as_text=True)
    assert "404" in text
    assert "Student Not Found" in text
