import os

def file_exists(filename):
    static_path = os.path.join(os.getcwd(), 'static', filename)
    return os.path.exists(static_path)