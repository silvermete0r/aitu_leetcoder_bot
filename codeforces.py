import requests
import time

########################
# Codeforces User Info #
########################

def get_codeforces_user(username):
  try:
    url = "https://codeforces.com/api/user.info?handles="
    response = requests.get(f"{url}{username}")
    if response.status_code != 200:
      return {"status": "error"}
    data = response.json()
    if data["status"] == "FAILED":
      return {"status": "error"}
  except Exception as e:
    print("Error in get_codeforces_user: ", e)
    data = {"status": "error"}
  finally:
    return data


def convert_seconds_to_days(seconds):
  current_time = round(time.time())
  days_in_codeforces = (current_time - seconds) // 86400
  return days_in_codeforces