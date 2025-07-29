from uuid import uuid4
import pytest

@pytest.mark.e2e
def test_register_and_login(page, fastapi_server):
    """Register a new user through the UI and then log in."""
    base_url = fastapi_server.rstrip('/')
    username = f"user_{uuid4().hex[:8]}"
    password = "ValidPass123!"

    # ----------------- Register -----------------
    page.goto(f"{base_url}/register")

    page.fill('#username', username)
    page.fill('#email', f"{username}@example.com")
    page.fill('#first_name', 'Test')
    page.fill('#last_name', 'User')
    page.fill('#password', password)
    page.fill('#confirm_password', password)

    page.click('button[type="submit"]')

    # Wait for success message and redirect
    page.wait_for_selector('#successAlert', state='visible')
    page.wait_for_timeout(2000)
    page.wait_for_url(f"{base_url}/login")

    # ----------------- Login -----------------
    page.fill('#username', username)
    page.fill('#password', password)
    page.click('button[type="submit"]')

    page.wait_for_selector('#successAlert', state='visible')
    page.wait_for_url(f"{base_url}/dashboard")

@pytest.mark.e2e
def test_register_short_password(page, fastapi_server):
    """Registration should fail client-side with a short password."""
    base_url = fastapi_server.rstrip('/')
    page.goto(f"{base_url}/register")

    page.fill('#username', 'shortuser')
    page.fill('#email', 'short@example.com')
    page.fill('#first_name', 'Short')
    page.fill('#last_name', 'User')
    page.fill('#password', 'short')
    page.fill('#confirm_password', 'short')
    page.click('button[type="submit"]')

    page.wait_for_selector('#errorAlert', state='visible')
    assert 'Password' in page.inner_text('#errorAlert')

@pytest.mark.e2e
def test_login_wrong_password(page, fastapi_server):
    """Attempting login with wrong password shows error."""
    base_url = fastapi_server.rstrip('/')
    username = f"user_{uuid4().hex[:8]}"
    password = "ValidPass123!"

    # register user directly via API
    import requests
    reg_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': f'{username}@example.com',
        'username': username,
        'password': password,
        'confirm_password': password
    }
    resp = requests.post(f"{base_url}/auth/register", json=reg_data)
    assert resp.status_code == 201

    page.goto(f"{base_url}/login")
    page.fill('#username', username)
    page.fill('#password', 'WrongPass1!')
    page.click('button[type="submit"]')

    page.wait_for_selector('#errorAlert', state='visible')
    assert 'Invalid' in page.inner_text('#errorAlert') or 'failed' in page.inner_text('#errorAlert')