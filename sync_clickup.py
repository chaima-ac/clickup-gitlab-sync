import os
import sys
import requests

API_TOKEN = os.environ.get("CLICKUP_TOKEN")

def get_task(task_id):
    url = f"https://api.clickup.com/api/v2/task/{task_id}"
    headers = {"Authorization": API_TOKEN}
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

def update_status(task_id, new_status):
    url = f"https://api.clickup.com/api/v2/task/{task_id}"
    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json"
    }
    body = {"status": new_status}
    response = requests.put(url, headers=headers, json=body)
    response.raise_for_status()
    print(f"Updated {task_id} to status: {new_status}")

if __name__ == "__main__":
    task_id = sys.argv[1]
    new_status = sys.argv[2]

    task = get_task(task_id)
    if not task:
        print(f"No task found with ID {task_id}")
        sys.exit(1)

    update_status(task_id, new_status)