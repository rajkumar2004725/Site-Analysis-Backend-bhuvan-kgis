import os
import sys

# Add the api directory to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
api_path = os.path.join(project_root, 'api')
sys.path.insert(0, api_path)  # Insert at the beginning to prioritize

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhuvan_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)