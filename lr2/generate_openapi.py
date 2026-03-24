import yaml
from main import app

openapi_data = app.openapi()

with open("openapi.yaml", "w", encoding="utf-8") as f:
    yaml.dump(openapi_data, f, sort_keys=False, allow_unicode=True)

print("Файл openapi.yaml успешно сгенерирован!")