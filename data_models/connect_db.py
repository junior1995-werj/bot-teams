from sqlalchemy import create_engine

from config import settings

engine = create_engine(settings.MYSQL_DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
