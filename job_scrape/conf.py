import os
import nltk
from pydantic import BaseSettings, Field
from functools import lru_cache

from nltk.corpus import stopwords



class Settings(BaseSettings):
    db_connection_str: str = Field(..., env='DB_CONNECTION_STR')
    # redis_url: str = Field(..., enc='REDIS_URL')

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()

@lru_cache
def cache_stopword():
    nltk.download('stopwords')
    nltk.download('punkt')
    stop_words = stopwords.words('english')
    return stop_words