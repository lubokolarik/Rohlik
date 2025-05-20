import os
import logging
import xml.etree.ElementTree as ET
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_time(timestamp):
    """Převede časový údaj z XML na objekt datetime."""
    try:
        return datetime.strptime(timestamp, "%Y%m%d %H:%M:%S.%f")
    except ValueError:
        logging.warning(f"Nepodařilo se převést čas {timestamp}, použiji výchozí hodnotu.")
        return datetime.utcnow()  # Použije aktuálny čas, ak konverzia zlyhá

# Načítání environment proměnných
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")

if not all([INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_BUCKET, INFLUXDB_ORG]):
    logging.error("Chybí environmentální proměnné!")
    logging.error(f"INFLUXDB_URL: {INFLUXDB_URL}")
    logging.error(f"INFLUXDB_BUCKET: {INFLUXDB_BUCKET}")
    logging.error(f"INFLUXDB_ORG: {INFLUXDB_ORG}")
    logging.error(f"INFLUXDB_TOKEN: {'HIDDEN' if INFLUXDB_TOKEN else 'MISSING'}")
    raise ValueError("Chyba: Chybí environmentální proměnné!")

logging.info(f"Připojení k InfluxDB na {INFLUXDB_URL}, bucket: {INFLUXDB_BUCKET}")
print(f"Připojení k InfluxDB na {INFLUXDB_URL}, bucket: {INFLUXDB_BUCKET}")

# Připojení k InfluxDB
try:
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api()
    logging.info("Připojení k InfluxDB bylo úspěšné.")
except Exception as e:
    logging.error(f"Chyba připojení k InfluxDB: {str(e)}")
    raise

# Promazání databáze
try:
    logging.info(f"Promazání dat v bucketu {INFLUXDB_BUCKET}...")
    delete_api = client.delete_api()
    delete_api.delete(
        start=datetime(1970, 1, 1),
        stop=datetime.utcnow(),
        bucket=INFLUXDB_BUCKET,
        org=INFLUXDB_ORG,
        predicate=""
    )
    logging.info(f"Data v bucketu {INFLUXDB_BUCKET} byla úspěšně smazána.")
except Exception as e:
    logging.error(f"Chyba při promazání databáze: {str(e)}")
    raise

# Načtení XML souboru
xml_file = "/usr/src/app/results/output.xml"
if not os.path.exists(xml_file):
    raise FileNotFoundError(f"Soubor {xml_file} neexistuje.")

tree = ET.parse(xml_file)
root = tree.getroot()

# Parsování statistik
statistics = root.find(".//statistics")
if statistics is None:
    logging.error("Nepodařilo se najít statistiky v `output.xml`.")
    raise ValueError("Nepodařilo se najít statistiky v `output.xml`.")

# Extrakce pro "All Tests"
total_stat = statistics.find(".//total/stat")
if total_stat is not None:
    total = int(total_stat.get("pass", 0)) + int(total_stat.get("fail", 0))
    passed = int(total_stat.get("pass", 0))
    failed = int(total_stat.get("fail", 0))
    elapsed_seconds = 0  # Hodnota pro "elapsed_seconds"

    point = Point("test_statistics") \
        .tag("category", "all_tests") \
        .field("total", total) \
        .field("passed", passed) \
        .field("failed", failed) \
        .field("elapsed_seconds", elapsed_seconds) \
        .time(datetime.utcnow(), WritePrecision.NS)

    logging.info(f"Odesílám: category=all_tests, total={total}, passed={passed}, failed={failed}, elapsed_seconds={elapsed_seconds}")
    print(f"Odesílám: category=all_tests, total={total}, passed={passed}, failed={failed}, elapsed_seconds={elapsed_seconds}")

    try:
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        logging.info("Data úspěšně zapsána do InfluxDB.")
    except Exception as e:
        logging.error(f"Chyba při zápisu do InfluxDB: {str(e)}")
        raise

# Extrakce podle Suite a Testy v rámci Suite
for suite in root.findall(".//suite"):
    suite_name = suite.get("name", "unknown").replace(" ", "_")
    start_time = parse_time(suite.get("starttime", ""))
    end_time = parse_time(suite.get("endtime", ""))

    if start_time and end_time:
        elapsed_seconds = int((end_time - start_time).total_seconds())
    else:
        elapsed_seconds = 0
        logging.warning(f"Varování: Nenalezen starttime/endtime pro {suite_name}, nastavujeme 0.")

    # Iterování cez všetky staty v rámci suite
    for stat in suite.findall(".//stat"):
        test_name = stat.get("name", "unknown").replace(" ", "_")
        category_name = test_name.replace("unknown.", "")

        passed = int(stat.get("pass", 0))
        failed = int(stat.get("fail", 0))
        skipped = int(stat.get("skip", 0))  # Ak existuje atribút "skip"
        total = passed + failed + skipped  # Celkový počet testov pre tento test

        point = Point("test_statistics") \
            .tag("category", category_name) \
            .field("total", total) \
            .field("passed", passed) \
            .field("failed", failed) \
            .field("elapsed_seconds", elapsed_seconds) \
            .time(datetime.utcnow(), WritePrecision.NS)

        logging.info(f"Odesílám: category={category_name}, total={total}, passed={passed}, failed={failed}, elapsed_seconds={elapsed_seconds}")
        print(f"Odesílám: category={category_name}, total={total}, passed={passed}, failed={failed}, elapsed_seconds={elapsed_seconds}")

        try:
            write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            logging.info("Data úspěšně zapsána do InfluxDB.")
        except Exception as e:
            logging.error(f"Chyba při zápisu do InfluxDB: {str(e)}")
            raise

# Uzavření write_api
write_api.close()
print("Skript úspěšně dokončen.")
