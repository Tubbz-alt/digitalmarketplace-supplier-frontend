import requests
from flask import json, current_app
from ..model import User


class ApiClient:
    root_url = None
    token = None

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.root_url = app.config['DM_API_URL']
        self.token = app.config['DM_API_AUTH_TOKEN']

    def headers(self):
        return {
            "content-type": "application/json",
            "Authorization": "Bearer {}".format(self.token)
        }

    def services_by_supplier_id(self, supplier_id):
        res = requests.get(
            "{}/{}?supplier_id={}".format(
                self.root_url,
                "services",
                supplier_id),
            headers=self.headers()
        )
        if res.status_code == 200:
            return res.json()
        else:
            current_app.logger.error("Error getting services for %s: %s - %s",
                                     supplier_id, res.status_code,
                                     res.json()["error"])
            return {"services": {}}

    def user_by_id(self, user_id):
        res = requests.get(
            "{}/{}/{}".format(self.root_url, "users", user_id),
            headers=self.headers()
        )
        if res.status_code == 200:
            return User.from_json(res.json())
        else:
            current_app.logger.error("Error getting user by id %s: %s - %s",
                                     user_id, res.status_code,
                                     res.json()["error"])
        return None

    def user_by_email(self, email_address):
        res = requests.get(
            "{}/{}".format(self.root_url, "users"),
            params={"email": email_address},
            headers=self.headers()
        )
        if res.status_code == 200:
            return User.from_json(res.json())
        elif res.status_code != 404:
            current_app.logger.error("Error getting user by email %s: %s - %s",
                                     email_address, res.status_code,
                                     res.json()["error"])
        return None

    def users_auth(self, email_address, password):
        res = requests.post(
            "{}/{}".format(self.root_url, "users/auth"),
            data=json.dumps(
                {
                    "authUsers": {
                        "emailAddress": email_address,
                        "password": password
                    }
                }
            ),
            headers=self.headers()
        )
        code = res.status_code
        if code == 200:
            # Only log in supplier users to this app
            if self.is_supplier_user(res.json()):
                return User.from_json(res.json())
            else:
                current_app.logger.info("Login by non-supplier user %s",
                                        email_address)
        elif code == 403:
            current_app.logger.info("Login failure for email %s: %s",
                                    email_address, res.status_code)
        elif code == 404:
            current_app.logger.info("Login not found for email %s: %s",
                                    email_address, res.status_code)
        else:
            current_app.logger.error("Error logging in email %s: %s",
                                     email_address, res.status_code)
        return None

    def user_update_password(self, user_id, new_password):
        res = requests.post(
            "{}/{}/{}".format(self.root_url, "users", user_id),
            data=json.dumps(
                {
                    "users": {
                        "password": new_password
                    }
                }
            ),
            headers=self.headers()
        )
        if res.status_code == 200:
            current_app.logger.info("Updated password for user %s", user_id)
            return True
        else:
            current_app.logger.info("Password update failed for user %s: %s",
                                    user_id, res.status_code)
            return False

    @staticmethod
    def is_supplier_user(user_json):
        if "supplier" in user_json["users"]:
            return True
        return False