import os
import sys
import requests

API_TOKEN = os.environ.get("CLICKUP_TOKEN")
print(f"Token length: {len(API_TOKEN) if API_TOKEN else 'None'}")
LIST_ID = "901220180810"

def get_task_by_cu_id(cu_id):
    url = f"https://api.clickup.com/api/v2/list/{LIST_ID}/task"
    headers = {"Authorization": API_TOKEN}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    tasks = response.json()["tasks"]

    for task in tasks:
        if task["name"].startswith(cu_id):
            return task["id"]
    return None

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
    cu_id = sys.argv[1]
    new_status = sys.argv[2]

    task_id = get_task_by_cu_id(cu_id)
    if not task_id:
        print(f"No task found matching {cu_id}")
        sys.exit(1)

    update_status(task_id, new_status)