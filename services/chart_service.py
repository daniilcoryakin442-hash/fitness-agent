# chart_service.py — график сна (matplotlib)

import io
import datetime
import matplotlib
matplotlib.use("Agg")  # без GUI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def build_sleep_chart(sleep_records: list, target: float = 8.0) -> bytes:
    """Построить PNG-график сна за 30 дней и вернуть байты."""
    if not sleep_records:
        return b""

    dates = [datetime.date.fromisoformat(r["date"]) for r in sleep_records]
    hours = [r["hours"] for r in sleep_records]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(dates, hours, color="#4A90D9", label="Сон (ч)")
    ax.axhline(y=target, color="#E74C3C", linestyle="--", linewidth=1.5,
               label=f"Норма ({target} ч)")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.xticks(rotation=45, fontsize=8)
    ax.set_ylabel("Часы сна")
    ax.set_title("📈 График сна за 30 дней")
    ax.legend()
    ax.set_ylim(0, max(hours + [target]) + 1)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
