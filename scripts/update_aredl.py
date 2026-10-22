
import json
import os
import urllib.request
from pathlib import Path

API_URLS = [
    "https://api.aredl.net/v2/levels",
    "https://api.aredl.net/api/aredl/levels",
]

OUTPUT = Path("data/aredl-levels.json")


def fetch_levels():
    errors = []

    for url in API_URLS:
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "AREDL-Data-Mirror/1.0"}
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))

            if isinstance(payload, dict):
                payload = payload.get("data", payload.get("levels", payload))

            if not isinstance(payload, list):
                raise ValueError("La respuesta no es una lista JSON.")

            levels = []

            for item in payload:
                if not isinstance(item, dict):
                    continue

                name = item.get("name") or item.get("title")
                position = item.get("position", item.get("rank"))

                if not name or position is None:
                    continue

                try:
                    position = int(position)
                except (TypeError, ValueError):
                    continue

                levels.append({
                    "id": item.get("id", item.get("level_id")),
                    "name": str(name).strip(),
                    "position": position
                })

            if not levels:
                raise ValueError(
                    "No se encontraron niveles con nombre y posición."
                )

            if len(levels) < 500:
                raise ValueError(
                    f"Solo se encontraron {len(levels)} niveles; "
                    "se cancela la actualización por seguridad."
                )

            levels.sort(key=lambda level: level["position"])

            positions = [level["position"] for level in levels]
            if len(positions) != len(set(positions)):
                raise ValueError("Hay posiciones duplicadas en la respuesta.")

            return levels

        except Exception as error:
            errors.append(f"{url}: {error}")

    raise RuntimeError(
        "No se pudo obtener una lista válida de AREDL:\n"
        + "\n".join(errors)
    )


def main():
    levels = fetch_levels()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(levels, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print(f"JSON actualizado: {len(levels)} niveles.")


if __name__ == "__main__":
    main()
