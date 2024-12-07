from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv
import os
import json

load_dotenv()

api = TodoistAPI(os.environ.get("TODOIST_API_TOKEN"))


def fetch_projects():
    print("\n\n### Fetching todo list")
    try:
        projects = api.get_projects()
        result = []

        for project in projects:
            tasks = api.get_tasks(project_id=project.id)

            project_data = {
                "project_id": project.id,
                "project_name": project.name,
                "tasks": [
                    {
                        "task_id": task.id,
                        "content": task.content,
                        "due_date": task.due.string if task.due else "No due date",
                        "is_completed": task.is_completed
                    }
                    for task in tasks
                ]
            }

            result.append(project_data)

        print(f"Projects: {json.dumps(result, indent=4)}")
        return {"message": "Projects fetched successfully", "projects": result}
    except Exception as error:
        error_message = f"Error fetching projects with tasks: {error}"
        print(error_message)
        return {"message": error_message}


def create_project(name):
    print(f"\n\n### Creating project: {name}")
    try:
        project = api.add_project(name=name)
        project_data = {
            "project_id": project.id,
            "project_name": project.name
        }
        print(f"Project created: {project_data}")
        return {"message": "Project created successfully", "project": project_data}
    except Exception as error:
        error_message = f"Error creating project: {error}"
        print(error_message)
        return {"message": error_message}


def create_task(name, project_id, description=None, due_string=None, priority=None):
    print("\n\n### Creating task")
    try:
        task_args = {
            'content': name,
            'project_id': project_id
        }
        if description is not None:
            task_args['description'] = description
        if due_string is not None:
            task_args['due_string'] = due_string
        if priority is not None:
            task_args['priority'] = priority

        print(f"Task arguments: {task_args}")

        task = api.add_task(**task_args)
        task_data = {
            "task_id": task.id,
            "content": task.content,
            "due_date": task.due.string if task.due else "No due date",
            "is_completed": task.is_completed
        }
        print(f"Task created: {task_data}")
        return {"message": "Task created successfully", "task": task_data}
    except Exception as error:
        error_message = f"Error creating task: {error}"
        print(error_message)
        return {"message": error_message}


def update_task_due_date(task_id, due_string):
    print(f"\n\n### Updating due date for task {task_id} to {due_string}")
    try:
        is_success = api.update_task(task_id=task_id, due_string=due_string)
        if is_success:
            msg = f"Due date for task {task_id} updated to {due_string}"
            print(msg)
            return {"message": msg}
        else:
            raise Exception("Update failed")
    except Exception as error:
        error_message = f"Error updating task {task_id}: {error}"
        print(error_message)
        return {"message": error_message}


def close_task(task_id):
    print(f"\n\n### Closing task {task_id}")
    try:
        is_success = api.close_task(task_id=task_id)
        if is_success:
            msg = f"Task {task_id} closed successfully"
            print(msg)
            return {"message": msg}
        else:
            raise Exception("Close operation failed")
    except Exception as error:
        error_message = f"Error closing task {task_id}: {error}"
        print(error_message)
        return {"message": error_message}


def delete_project(project_id):
    print(f"\n\n### Deleting project {project_id}")
    try:
        is_success = api.delete_project(project_id=project_id)
        if is_success:
            msg = f"Project {project_id} deleted successfully"
            print(msg)
            return {"message": msg}
        else:
            raise Exception("Delete operation failed")
    except Exception as error:
        error_message = f"Error deleting project {project_id}: {error}"
        print(error_message)
        return {"message": error_message}
