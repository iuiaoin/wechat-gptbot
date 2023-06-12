import datetime
import requests
from config import conf

class QueryKey(object) :

    def get_key():
        api_base = conf().get("openai_api_base")
        if api_base:
            api_base = api_base
        else:
            api_base = "https://api.openai.com/v1"
        subscription_url = api_base+"/dashboard/billing/subscription"
        headers = {"Authorization": "Bearer " + conf().get("openai_api_key"),
                "Content-Type": "application/json"}
        subscription_response = requests.get(subscription_url, headers=headers)
        if subscription_response.status_code == 200:
            data = subscription_response.json()
            total = data.get("hard_limit_usd")
        else:
            return subscription_response.text
        # Set start_date to 99 days before today’s date.
        start_date = (datetime.datetime.now() - datetime.timedelta(days=99)).strftime("%Y-%m-%d")
        # Set end_date to today’s date plus 1 day.
        end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        billing_url = api_base + f"/dashboard/billing/usage?start_date={start_date}&end_date={end_date}"
        billing_response = requests.get(billing_url, headers=headers)
        if billing_response.status_code == 200:
            data = billing_response.json()
            total_usage = data.get("total_usage") / 100
            daily_costs = data.get("daily_costs")
            days = min(conf().get("recent_days"), len(daily_costs))
            recent = f"### Usage in the last {days} days  \n"
            for i in range(days):
                cur = daily_costs[-i - 1]
                date = datetime.datetime.fromtimestamp(cur.get("timestamp")).strftime("%Y-%m-%d")
                line_items = cur.get("line_items")
                cost = 0
                for item in line_items:
                    cost += item.get("cost")
                recent += f"\t{date}\t{(cost / 100):.2f} \n"
        else:
            return billing_response.text

        return f"## Total:\t{total:.2f}$  \n" \
               f"## Used:\t{total_usage:.2f}$  \n" \
               f"## Remaining:\t{total - total_usage:.2f}$  \n" \
               f"\n" + recent
