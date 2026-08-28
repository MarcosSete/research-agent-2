from app.config.settings import settings
from app.config.profile import load_research_profile

print(settings.database_url)
print(settings.deepseek_api_key)

profile = load_research_profile()

print(profile.interests)
print(profile.priority["Deep Learning"])