class Config:
    """Stores configuration like API keys and other settings."""
    STABLE_DIFFUSION_API_KEY = None  # Your API key here
    API_KEY = "YOUR_API_KEY_HERE"
    BASE_URL = "https://api.deepseek.com"
    MODEL_NAME = "deepseek-chat"

    # API_KEY = "EMPTY"
    # BASE_URL = "http://localhost:8000/v1"
    # MODEL_NAME = "Qwen2.5-72B-Instruct"
    NGROK_URL = "https://b201-58-144-141-64.ngrok-free.app"

    @staticmethod
    def print_config():
        """For debugging purposes, prints the current configuration values."""
        print(f"API_KEY: {Config.STABLE_DIFFUSION_API_KEY}")
        print(f"API_SECRET: {Config.DEEPSEEK_API_KEY}")
        # print(f"BASE_URL: {Config.BASE_URL}")
        # print(f"DEBUG: {Config.DEBUG}")
