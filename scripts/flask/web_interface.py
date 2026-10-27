import asyncio
import os
import subprocess
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
    next_cmd,
)
from werkzeug.utils import secure_filename

PRINTER_IP = os.environ.get("PRINTER_IP", "127.0.0.1")
UPLOAD_FOLDER = "/tmp/uploads"
SNMP_COMMUNITY = "public"
BASE_OID = "1.3.6.1.2.1.43.11.1.1"

app = Flask(__name__, static_folder="/home/flask/static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default-secret")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def read_version():
    try:
        with open("/VERSION") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading VERSION file: {e}")
        return "Unknown"


def get_cronjob_description():
    try:
        result = subprocess.run(
            ["/home/describe_cron.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout
    except Exception as e:
        return f"Failed to get cronjob description: {e}"


async def _snmp_get(oid):
    engine = SnmpEngine()
    transport = await UdpTransportTarget.create((PRINTER_IP, 161), timeout=1, retries=2)
    errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
        engine,
        CommunityData(SNMP_COMMUNITY, mpModel=0),
        transport,
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )
    engine.close_dispatcher()
    if errorIndication or errorStatus:
        return None
    for varBind in varBinds:
        return varBind[1].prettyPrint()
    return None


async def _snmp_table(oid):
    result = {}
    engine = SnmpEngine()
    transport = await UdpTransportTarget.create((PRINTER_IP, 161), timeout=1, retries=2)
    initial_oid = oid
    current_oid = ObjectType(ObjectIdentity(oid))
    while True:
        errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
            engine,
            CommunityData(SNMP_COMMUNITY, mpModel=0),
            transport,
            ContextData(),
            current_oid,
        )
        if errorIndication or errorStatus or not varBinds:
            break
        for varBind in varBinds:
            oid_str = str(varBind[0])
            if not oid_str.startswith(initial_oid):
                engine.close_dispatcher()
                return result
            index = ".".join(oid_str.split(".")[len(initial_oid.split(".")) :])
            result[index] = varBind[1].prettyPrint()
            current_oid = ObjectType(ObjectIdentity(oid_str))
    engine.close_dispatcher()
    return result


def get_snmp_value(oid):
    return asyncio.run(_snmp_get(oid))


def get_snmp_table(oid):
    return asyncio.run(_snmp_table(oid))


@app.route("/")
def index():
    version = read_version()
    current_year = datetime.now().year
    cronjob_description = get_cronjob_description()
    return render_template(
        "index.html",
        version=version,
        year=current_year,
        cronjob_description=cronjob_description,
    )


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or not file.filename.endswith(".pdf"):
        return jsonify(success=False, message="Invalid file. Please upload a PDF.")
    sanitized_filename = secure_filename(file.filename)
    filepath = os.path.normpath(os.path.join(app.config["UPLOAD_FOLDER"], sanitized_filename))
    if not filepath.startswith(app.config["UPLOAD_FOLDER"]):
        return jsonify(success=False, message="Invalid file path.")
    file.save(filepath)
    try:
        subprocess.run(["/usr/bin/lp", "-d", "MyPrinter", filepath], check=True, capture_output=True, text=True)
        return jsonify(success=True, message="PDF sent to printer.")
    except subprocess.CalledProcessError as e:
        return jsonify(success=False, message=f"Failed to print PDF. Error: {e.stderr}")


@app.route("/print-color-page", methods=["POST"])
def print_color_page():
    try:
        subprocess.run(["/usr/local/bin/weekly_print.sh"], check=True, capture_output=True, text=True)
        return jsonify(success=True, message="Print color job sent.")
    except subprocess.CalledProcessError as e:
        return jsonify(success=False, message=f"Failed to send print color job. Error: {e.stderr}")


@app.route("/print-empty-test", methods=["POST"])
def print_empty_test():
    try:
        subprocess.run(["/home/test_empty.sh"], check=True, capture_output=True, text=True)
        return jsonify(success=True, message="Empty test page print job sent.")
    except subprocess.CalledProcessError as e:
        return jsonify(success=False, message=f"Failed to send empty test page print job. Error: {e.stderr}")


@app.route("/status")
def status():
    try:
        out = subprocess.check_output(["/usr/bin/lpstat", "-p", "MyPrinter"], text=True)
        return jsonify(success=True, status=out)
    except subprocess.CalledProcessError:
        return jsonify(success=False, status="Could not fetch printer status.")


@app.route("/ink-levels")
def ink_levels():
    try:
        descriptions = get_snmp_table(BASE_OID + ".6.1")
        levels = get_snmp_table(BASE_OID + ".9.1")
        ink_data = [{"name": descriptions[i], "level": int(levels.get(i, 0))} for i in sorted(descriptions.keys())]
        return jsonify(success=True, ink_data=ink_data)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@app.route("/device-info")
def device_info():
    try:
        device_oids = {
            "Model": "1.3.6.1.2.1.43.5.1.1.16.1",
            "Serial Number": "1.3.6.1.2.1.43.5.1.1.17.1",
            "Firmware Version": "1.3.6.1.2.1.43.5.1.1.18.1",
            "System Description": "1.3.6.1.2.1.1.1.0",
            "System Name": "1.3.6.1.2.1.1.5.0",
            "System Location": "1.3.6.1.2.1.1.6.0",
            "Contact": "1.3.6.1.2.1.1.4.0",
            "Device Description": "1.3.6.1.2.1.25.3.2.1.3.1",
        }
        info = {k: get_snmp_value(v) for k, v in device_oids.items()}
        return jsonify(success=True, device_info=info)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@app.route("/alerts")
def alerts():
    try:
        alert_descriptions = get_snmp_table("1.3.6.1.2.1.43.16.5.1.2")
        return jsonify(success=True, alert_descriptions=list(alert_descriptions.values()))
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
