# export_service.py — экспорт данных пользователя в CSV

import io
import csv
from db.measurements import get_weight_history, get_sleep_history

def export_user_data(user_id: int) -> bytes:
    """Собрать данные пользователя в CSV и вернуть байты."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Вес
    writer.writerow(["=== ВЕС ==="])
    writer.writerow(["Дата", "Вес (кг)"])
    for row in get_weight_history(user_id, 365):
        writer.writerow([row["date"], row["weight"]])

    writer.writerow([])

    # Сон
    writer.writerow(["=== СОН ==="])
    writer.writerow(["Дата", "Часы сна"])
    for row in get_sleep_history(user_id, 365):
        writer.writerow([row["date"], row["hours"]])

    output.seek(0)
    return output.read().encode("utf-8-sig")  # BOM для Excel
