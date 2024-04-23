import os
from envparse import env
import yaml
import requests

# Retrieve the API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

def has_env_example_changed():
    output = os.popen('git diff --name-only HEAD HEAD~1').read()
    return '.env.example' in output

def check_missing_env_vars():
    # Load .env.example variables
    example_vars = set()
    with open('.env.example', 'r') as file:
        for line in file:
            if '=' in line:
                key = line.split('=')[0].strip()
                example_vars.add(key)
    
    # Check all python files for missing env vars
    missing_vars = set()
    for subdir, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(subdir, file), 'r') as f:
                    content = f.read()
                    used_vars = set(env.findall(content))
                    missing_vars.update(used_vars - example_vars)

    return missing_vars

def check_new_migrations():
    output = os.popen('git diff --name-only HEAD HEAD~1').read()
    return any('migrations/' in line for line in output.split('\n'))

def send_notification(message):
    url = 'https://api.notification.service/send'
    headers = {'Authorization': f'Bearer {api_key}'}
    data = {'message': message}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

if __name__ == "__main__":
    env_example_changed = has_env_example_changed()
    missing_vars = check_missing_env_vars()
    new_migration = check_new_migrations()

    if env_example_changed:
        send_notification("The .env.example file has changed.")
    if missing_vars:
        send_notification("Missing env variables: " + ', '.join(missing_vars))
    if new_migration:
        send_notification("New files have been added to the migrations folder.")
