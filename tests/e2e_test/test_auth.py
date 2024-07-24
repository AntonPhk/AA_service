import pytest
from tests.utils import fake_factory
from additional_services.mail_sender import EmailSender


class MockEmailSender:
    async def send_accept_registration_email(self, *args, **kwargs):
        return True

    async def send_reset_password_email(self, *args, **kwargs):
        return True


@pytest.mark.asyncio
class TestAuth:
    async def test_signup(self, client, monkeypatch):
        monkeypatch.setattr(
            EmailSender,
            "send_accept_registration_email",
            MockEmailSender.send_accept_registration_email,
        )

        user = fake_factory.generate_base_user()
        user["id"] = str(user["id"])
        print(user["id"])
        resp = await client.post("/api/auth/signup", json=user)
        resp_json = resp.json()
        assert resp.status_code == 201
        assert resp_json == {"message": "To confirm registration, check your email."}

    @pytest.mark.parametrize("add_user", ["base"], indirect=True)
    async def test_confirm_registration(self, client, get_access_token):
        resp = await client.get(
            f"/api/auth/confirm_registration?token={get_access_token}"
        )
        resp_json = resp.json()
        assert resp.status_code == 200
        assert resp_json == {"message": "Registration confirmed."}

    @pytest.mark.parametrize("add_user", ["verified"], indirect=True)
    async def test_login(self, client, add_user):
        resp = await client.post(
            "/api/auth/login",
            data={"username": add_user["username"], "password": add_user["password"]},
        )
        resp_json = resp.json()
        assert resp.status_code == 200
        assert resp_json["access_token"] and resp_json["refresh_token"]

    @pytest.mark.parametrize("add_user", ["verified"], indirect=True)
    async def test_change_password(self, client, login_fake_user):
        new_password = {"password": "qwerty123"}
        headers = {"Authorization": f"Bearer {login_fake_user['access_token']}"}
        resp = await client.post(
            "/api/auth/change_password", headers=headers, json=new_password
        )
        resp_json = resp.json()
        assert resp.status_code == 200
        assert resp_json["detail"] == "Password changed successfully."

    @pytest.mark.parametrize("add_user", ["verified"], indirect=True)
    async def test_request_reset_password(self, client, add_user, monkeypatch):
        monkeypatch.setattr(
            EmailSender,
            "send_reset_password_email",
            MockEmailSender.send_reset_password_email,
        )

        email = add_user["email"]
        resp = await client.get(f"/api/auth/request_reset_password?email={email}")
        resp_json = resp.json()
        assert resp.status_code == 200
        assert resp_json == {"message": "To reset your password, check your email."}

    @pytest.mark.parametrize("add_user", ["base"], indirect=True)
    async def test_reset_password(self, client, get_access_token):
        resp = await client.get(f"/api/auth/reset_password?token={get_access_token}")
        resp_json = resp.json()
        assert resp.status_code == 200
        assert (
            "Password has been reset successfully. New password is"
            in resp_json["message"]
        )
