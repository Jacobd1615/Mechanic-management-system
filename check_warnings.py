#!/usr/bin/env python3
import warnings
import sys

# Capture all warnings
warnings.filterwarnings("always")


# Redirect warnings to stdout so we can see them
def warn_with_traceback(message, category, filename, lineno, file=None, line=None):
    log = file if hasattr(file, "write") else sys.stderr
    log.write(f"Warning: {category.__name__}: {message}\n")
    log.write(f"  File: {filename}, line {lineno}\n")
    if line:
        log.write(f"  Code: {line.strip()}\n")
    log.write("\n")


warnings.showwarning = warn_with_traceback

print("Starting app import...")
try:
    from app import create_app

    print("App imported successfully")

    print("Creating app...")
    app = create_app("TestingConfig")
    print("App created successfully")

    print("Testing app context...")
    with app.app_context():
        from app.models import db, Mechanic

        print("Models imported successfully")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
