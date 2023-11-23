from prettyconf import config

class Settings:

    APP_ID = config("APP_ID")
    APP_PASSWORD = config("APP_PASSWORD")
    PORT = config("PORT")
    URL_TOP_DESK = config("URL_TOP_DESK")
    USER_TOP_DESK = config("USER_TOP_DESK")
    PASSWORD_TOP_DESK = config("PASSWORD_TOP_DESK")
    MYSQL_DATABASE_URL = config("MYSQL_DATABASE_URL")
    IGNORED_ENDPOINTS= config("IGNORED_ENDPOINTS")
    SECRET_KEY = config("SECRET_KEY")

settings = Settings()