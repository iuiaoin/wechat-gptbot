import requests
from config import conf


class QueryKey(object):
    def get_key():
        api_base = conf().get("openai_api_base")
        if api_base:
            api_base = api_base
        else:
            api_base = "https://api.openai.com/v1"
        subscription_url = api_base + "/dashboard/billing/credit_grants"
        headers = {
            "Authorization": "Bearer " + conf().get("openai_sensitive_id"),
            "Content-Type": "application/json",
        }
        subscription_response = requests.get(subscription_url, headers=headers)
        if subscription_response.status_code == 200:
            data = subscription_response.json()
            total_granted = data.get("total_granted")
            total_used = data.get("total_used")
            total_available = data.get("total_available")
        else:
            return subscription_response.text

        return (
            f"## Total:\t{total_granted:.2f}$  \n"
            f"## Used:\t{total_used:.2f}$  \n"
            f"## Available:\t{total_available:.2f}$  \n"
        )
