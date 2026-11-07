"""
Phase A Architectural Validation Suite:
Cloud Persistence, SQLAlchemy 2.0 ORM, JWT Authentication & Multi-Tenant Isolation
Location: test_auth_and_persistence.py
"""
import uuid
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db, SessionLocal
from app.models.user import User
from app.models.project import Project

# Initialize test client and database tables
init_db()
client = TestClient(app)

print("\n" + "=" * 70)
print("     STARTING SKETCH2UI PHASE A AUTH & PERSISTENCE TEST SUITE")
print("=" * 70)

test_suffix = uuid.uuid4().hex[:8]
user_a_email = f"user_a_{test_suffix}@example.com"
user_b_email = f"user_b_{test_suffix}@example.com"
common_password = "SecurePassword123!"

# ----------------------------------------------------------------------
# Test 1: User Registration & Token Minting
# ----------------------------------------------------------------------
print("\n--- Test 1: User Signup & JWT Generation ---")

signup_payload = {
    "email": user_a_email,
    "password": common_password,
    "name": "User Alpha"
}
res_signup = client.post("/api/v1/auth/signup", json=signup_payload)
assert res_signup.status_code == 201, f"Signup failed: {res_signup.text}"
data_signup = res_signup.json()

assert "access_token" in data_signup, "No access_token returned on signup"
assert data_signup["token_type"] == "bearer", f"Expected bearer token_type, got {data_signup['token_type']}"
assert data_signup["user"]["email"] == user_a_email
assert data_signup["user"]["tier"] == "free"
assert "id" in data_signup["user"]
user_a_token = data_signup["access_token"]
user_a_id = data_signup["user"]["id"]
print(f"  [OK] User signed up successfully with ID: {user_a_id}")
print(f"  [OK] Bearer token received: {user_a_token[:25]}...")

# Duplicate registration check
res_dup = client.post("/api/v1/auth/signup", json=signup_payload)
assert res_dup.status_code == 400, f"Expected 400 for duplicate email, got {res_dup.status_code}"
print("  [OK] Duplicate email rejected with HTTP 400")

# ----------------------------------------------------------------------
# Test 2: User Login & Invalid Credentials Guardrail
# ----------------------------------------------------------------------
print("\n--- Test 2: User Login & Verification ---")

# Valid Login
login_payload = {
    "email": user_a_email,
    "password": common_password
}
res_login = client.post("/api/v1/auth/login", json=login_payload)
assert res_login.status_code == 200, f"Login failed: {res_login.text}"
data_login = res_login.json()
assert "access_token" in data_login
assert data_login["user"]["id"] == user_a_id
print("  [OK] Successful authentication and token issuance")

# Invalid Password Login
res_bad_pw = client.post("/api/v1/auth/login", json={"email": user_a_email, "password": "WrongPassword"})
assert res_bad_pw.status_code == 401, f"Expected 401 for wrong password, got {res_bad_pw.status_code}"
print("  [OK] Invalid password correctly rejected with HTTP 401")

# ----------------------------------------------------------------------
# Test 3: Authenticated /api/v1/auth/me Profile Check
# ----------------------------------------------------------------------
print("\n--- Test 3: Authenticated Profile (/api/v1/auth/me) ---")

res_me = client.get(
    "/api/v1/auth/me",
    headers={"Authorization": f"Bearer {user_a_token}"}
)
assert res_me.status_code == 200, f"Profile lookup failed: {res_me.text}"
me_data = res_me.json()
assert me_data["email"] == user_a_email
assert me_data["id"] == user_a_id
print(f"  [OK] Profile retrieved for user: {me_data['name']} ({me_data['email']})")

# Unauthenticated access to /me must fail with 401
res_unauth = client.get("/api/v1/auth/me")
assert res_unauth.status_code == 401, f"Expected 401 without auth, got {res_unauth.status_code}"
print("  [OK] Unauthenticated access rejected with HTTP 401")

# ----------------------------------------------------------------------
# Test 4: Multi-Tenant Project Isolation (User A vs User B)
# ----------------------------------------------------------------------
print("\n--- Test 4: Multi-Tenant Project Isolation ---")

# Register User B
res_signup_b = client.post(
    "/api/v1/auth/signup",
    json={"email": user_b_email, "password": common_password, "name": "User Beta"}
)
assert res_signup_b.status_code == 201
user_b_token = res_signup_b.json()["access_token"]
user_b_id = res_signup_b.json()["user"]["id"]

# User A creates a project
project_a_payload = {
    "title": "Alpha Dashboard Wireframe",
    "thumbnail_url": "data:image/png;base64,alpha_sample",
    "ast_json": {"elements": [{"type": "button", "label": "Alpha Action"}]},
    "jsx_code": "export default function Alpha() { return <button>Alpha</button>; }",
    "tailwind_code": "p-4 bg-zinc-900"
}
res_proj_a = client.post(
    "/api/v1/projects",
    json=project_a_payload,
    headers={"Authorization": f"Bearer {user_a_token}"}
)
assert res_proj_a.status_code == 201, f"Project creation failed: {res_proj_a.text}"
proj_a_data = res_proj_a.json()
proj_a_id = proj_a_data["id"]
assert proj_a_data["user_id"] == user_a_id
assert proj_a_data["title"] == "Alpha Dashboard Wireframe"
print(f"  [OK] User A created project with ID: {proj_a_id}")

# User B creates a project
project_b_payload = {
    "title": "Beta Landing Wireframe",
    "thumbnail_url": "data:image/png;base64,beta_sample",
    "ast_json": {"elements": [{"type": "heading", "text": "Beta Wireframe"}]},
    "jsx_code": "export default function Beta() { return <h1>Beta</h1>; }",
    "tailwind_code": "text-2xl font-bold"
}
res_proj_b = client.post(
    "/api/v1/projects",
    json=project_b_payload,
    headers={"Authorization": f"Bearer {user_b_token}"}
)
assert res_proj_b.status_code == 201
proj_b_id = res_proj_b.json()["id"]
print(f"  [OK] User B created project with ID: {proj_b_id}")

# Verify User A only sees User A's project
res_list_a = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {user_a_token}"})
assert res_list_a.status_code == 200
projs_a = res_list_a.json()
a_ids = [p["id"] for p in projs_a]
assert proj_a_id in a_ids, "User A project not in User A's list"
assert proj_b_id not in a_ids, "Data leak! User B's project appeared in User A's list"
print("  [OK] User A listing properly isolated (User B projects hidden)")

# Verify User B only sees User B's project
res_list_b = client.get("/api/v1/projects", headers={"Authorization": f"Bearer {user_b_token}"})
assert res_list_b.status_code == 200
projs_b = res_list_b.json()
b_ids = [p["id"] for p in projs_b]
assert proj_b_id in b_ids, "User B project not in User B's list"
assert proj_a_id not in b_ids, "Data leak! User A's project appeared in User B's list"
print("  [OK] User B listing properly isolated (User A projects hidden)")

# ----------------------------------------------------------------------
# Test 5: Tenant Security Guardrails (Unauthorized Access & Deletion)
# ----------------------------------------------------------------------
print("\n--- Test 5: Tenant Access & Modification Guardrails ---")

# User B tries to read User A's project -> 403 Forbidden
res_forbidden_get = client.get(
    f"/api/v1/projects/{proj_a_id}",
    headers={"Authorization": f"Bearer {user_b_token}"}
)
assert res_forbidden_get.status_code == 403, f"Expected 403, got {res_forbidden_get.status_code}"
print("  [OK] User B prevented from viewing User A's project (HTTP 403)")

# User B tries to delete User A's project -> 403 Forbidden
res_forbidden_del = client.delete(
    f"/api/v1/projects/{proj_a_id}",
    headers={"Authorization": f"Bearer {user_b_token}"}
)
assert res_forbidden_del.status_code == 403, f"Expected 403, got {res_forbidden_del.status_code}"
print("  [OK] User B prevented from deleting User A's project (HTTP 403)")

# User A successfully updates their project
res_update_a = client.put(
    f"/api/v1/projects/{proj_a_id}",
    json={"title": "Updated Alpha Wireframe", "tailwind_code": "p-6 bg-black"},
    headers={"Authorization": f"Bearer {user_a_token}"}
)
assert res_update_a.status_code == 200
assert res_update_a.json()["title"] == "Updated Alpha Wireframe"
print("  [OK] User A successfully updated project metadata")

# User A successfully deletes their project
res_del_a = client.delete(
    f"/api/v1/projects/{proj_a_id}",
    headers={"Authorization": f"Bearer {user_a_token}"}
)
assert res_del_a.status_code == 200
print("  [OK] User A successfully deleted project")

# ----------------------------------------------------------------------
# Test 6: Graceful Guest Mode Fallback
# ----------------------------------------------------------------------
print("\n--- Test 6: Graceful Guest Mode Fallback ---")

# Guest creates a project without any Authorization header
guest_payload = {
    "title": "Guest Anonymous Wireframe",
    "jsx_code": "<p>Guest Component</p>",
    "tailwind_code": "text-sm text-zinc-400"
}
res_guest_create = client.post("/api/v1/projects", json=guest_payload)
assert res_guest_create.status_code == 201, f"Guest project creation failed: {res_guest_create.text}"
guest_proj = res_guest_create.json()
assert guest_proj["user_id"] is None, "Guest project should have user_id=None"
guest_proj_id = guest_proj["id"]
print(f"  [OK] Guest project created successfully with user_id=None (ID: {guest_proj_id})")

# Guest lists projects without any Authorization header
res_guest_list = client.get("/api/v1/projects")
assert res_guest_list.status_code == 200, f"Guest listing failed: {res_guest_list.text}"
guest_projects = res_guest_list.json()
guest_ids = [p["id"] for p in guest_projects]
assert guest_proj_id in guest_ids, "Guest project should be visible in guest list"
assert proj_b_id not in guest_ids, "Registered user projects must not leak to unauthenticated guest list"
print("  [OK] Guest list returns guest projects without leaking registered user data")

print("\n" + "=" * 70)
print("     ALL PHASE A AUTH & PERSISTENCE TESTS PASSED SUCCESSFULLY!    ")
print("=" * 70 + "\n")
