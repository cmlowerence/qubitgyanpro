from services.telegram_service import send_telegram_message

def send_welcome_message(data):
    user = data.get("user")
    password = data.get("password")

    send_telegram_message(
        user.telegram_chat_id,
        f"Welcome! Your account is ready.\nPassword: {password}"
    )

def log_admission(data):
    print(f"Admission approved for {data.get('user')}")