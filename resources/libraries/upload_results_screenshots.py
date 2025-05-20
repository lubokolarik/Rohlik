import os
import logging
import xml.etree.ElementTree as ET
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Načítání environment proměnných
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")

if not all([INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_BUCKET, INFLUXDB_ORG]):
    logging.error("Chybí environmentální proměnné!")
    raise ValueError("Chyba: Chybí environmentální proměnné!")

logging.info(f"Připojení k InfluxDB na {INFLUXDB_URL}, bucket: {INFLUXDB_BUCKET}")

# Připojení k InfluxDB
try:
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api()
    logging.info("Připojení k InfluxDB bylo úspěšné.")
except Exception as e:
    logging.error(f"Chyba připojení k InfluxDB: {str(e)}")
    raise

# Načtení XML souboru
xml_file = "/usr/src/app/results/output.xml"
if not os.path.exists(xml_file):
    raise FileNotFoundError(f"Soubor {xml_file} neexistuje.")

tree = ET.parse(xml_file)
root = tree.getroot()

def extract_test_results(root):
    """Extrahuje název testu, status a důvod selhání z XML."""
    test_results = []
    for test in root.findall(".//test"):
        test_name = test.get("name", "Unknown Test")

        # Najdeme status testu
        status_element = test.find("./status")
        test_status = status_element.get("status") if status_element is not None else "UNKNOWN"

        # Pokud test selhal, najdeme důvod selhání
        failure_message = status_element.text.strip() if test_status == "FAIL" and status_element is not None else "None"

        test_results.append((test_name, test_status, failure_message))

    return test_results

def extract_test_statistics(root):
    """Extrahuje souhrnné statistiky testů z XML."""
    stat_element = root.find(".//stat")
    if stat_element is not None:
        pass_count = int(stat_element.get("pass", 0))
        fail_count = int(stat_element.get("fail", 0))
        skip_count = int(stat_element.get("skip", 0))
        total_tests = pass_count + fail_count + skip_count
        return pass_count, fail_count, skip_count, total_tests
    return 0, 0, 0, 0

# Získání výsledků testů
test_results = extract_test_results(root)

# Ukládání výsledků testů do InfluxDB
for test_name, test_status, failure_message in test_results:
    point = Point("test_results") \
        .tag("test_name", test_name) \
        .field("status", test_status) \
        .field("failure_message", failure_message) \
        .time(datetime.utcnow(), WritePrecision.NS)

    logging.info(f"Odesílám: test_name={test_name}, status={test_status}, failure_message={failure_message}")

    try:
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        logging.info("Data úspěšně zapsána do InfluxDB.")
    except Exception as e:
        logging.error(f"Chyba při zápisu do InfluxDB: {str(e)}")
        raise

# Získání testovacích statistik a jejich zápis do InfluxDB
pass_count, fail_count, skip_count, total_tests = extract_test_statistics(root)
if total_tests > 0:
    point = Point("test_statistics") \
        .field("pass", pass_count) \
        .field("fail", fail_count) \
        .field("skip", skip_count) \
        .field("total", total_tests) \
        .time(datetime.utcnow(), WritePrecision.NS)

    logging.info(f"Odesílám statistiky: pass={pass_count}, fail={fail_count}, skip={skip_count}, total={total_tests}")

    try:
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        logging.info("Statistiky úspěšně zapsány do InfluxDB.")
    except Exception as e:
        logging.error(f"Chyba při zápisu statistik do InfluxDB: {str(e)}")
        raise

# Uzavření write_api
write_api.close()
print("Skript úspěšně dokončen.")
