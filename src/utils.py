def validate_url(url):
    return url.startswith("https://github.com/") and url.endswith(".git")

def log_message(message):
    print(f"[LOG]: {message}")