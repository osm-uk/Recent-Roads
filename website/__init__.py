import csv
import json

import psycopg2
from flask import Flask, render_template

app = Flask(__name__, static_url_path="", static_folder="static")
conn = psycopg2.connect("dbname=rr user=rr")

authority_map = {}
with open("USRN Ranges.csv") as file:
    for row in csv.DictReader(file):
        authority_map[row["Local Custodian Code"]] = row


@app.route("/")
def home() -> str:
    return render_template("index.html", authorities=authority_map.values())


@app.route("/usrn/<usrn>")
def usrn(usrn: str) -> str:
    try:
        usrn_cleaned = int(usrn)
    except ValueError:
        return "Bad USRN"
    cur = conn.cursor()
    cur.execute(
        "SELECT street_type, CAST(usrn as varchar) as usrn, ST_AsGeoJSON(geometry) as geom FROM usrn WHERE usrn = %s LIMIT 1",
        (usrn_cleaned,),
    )
    record = cur.fetchone()
    cur.close()

    if not record:
        return ":( not found"

    geom = json.loads(record[2])
    if geom["type"] == "MultiLineString":
        lon, lat = geom["coordinates"][0][0]
    elif geom["type"] == "LineString":
        lon, lat = geom["coordinates"][0]
    else:
        raise Exception(geom)

    return render_template(
        "usrn.html", street_type=record[0], usrn=record[1], geom=geom, lat=lat, lon=lon
    )


@app.route("/authority/<authority>")
def authority(authority: str) -> str:
    authority_range = authority_map.get(authority)
    if not authority_range:
        return "Bad Authority"

    cur = conn.cursor()
    cur.execute(
        "SELECT street_type, usrn FROM usrn WHERE usrn > %s AND usrn < %s AND street_type != 'Numbered Street' ORDER BY usrn DESC LIMIT 100 OFFSET 0",
        (authority_range["USRN Start"], authority_range["USRN End"]),
    )
    records = cur.fetchall()
    cur.close()
    if not records:
        return ":( not found"

    return render_template("authority.html", usrns=records)
