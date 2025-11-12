import csv
import json
import os
import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__, static_url_path="", static_folder="static")
conn = psycopg2.connect(os.environ.get("DATABASE_URI"))

authority_map = {}
with open("USRN Ranges.csv") as file:
    for row in csv.DictReader(file):
        authority_map[row["Local Custodian Code"]] = row

lang_map = {
    None: "name",
    "cym": "name:cy",
    "gla": "name:gd",
    "eng": "name:en",
}


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
        "SELECT DISTINCT name_1, name_1_lang, name_2, name_2_lang FROM toid2name WHERE road_name_toid IN (SELECT toid FROM usrn2toid WHERE usrn=%s)",
        (usrn_cleaned,),
    )
    names = {}
    for name_1, name_1_lang, name_2, name_2_lang in cur.fetchall():
        if name_1:
            names[lang_map[name_1_lang]] = name_1
        if name_2:
            names[lang_map[name_2_lang]] = name_2

    cur.execute(
        "SELECT street_type, CAST(usrn as varchar) as usrn, ST_AsGeoJSON(geometry) as geom FROM usrn WHERE usrn = %s LIMIT 1",
        (usrn_cleaned,),
    )
    record = cur.fetchone()

    if not record:
        return ":( not found"

    usrn_geom = json.loads(record[2])
    if usrn_geom["type"] == "MultiLineString":
        lon, lat = usrn_geom["coordinates"][0][0]
    elif usrn_geom["type"] == "LineString":
        lon, lat = usrn_geom["coordinates"][0]
    else:
        raise Exception(usrn_geom)

    if "uprn" in request.args:
        cur.execute(
            """SELECT
					json_build_object(
						'type', 'FeatureCollection',
						'features', json_agg(
							ST_AsGeoJSON(t.*):: json
						)
					)
				FROM
					(
						SELECT
							uprn.uprn as "ref:GB:uprn",
							wkb_geometry
						FROM
							uprn2usrn
							JOIN uprn ON uprn.uprn = uprn2usrn.uprn
						WHERE
							uprn2usrn.usrn = %s
					) as t;""",
            (usrn_cleaned,),
        )
        uprns = cur.fetchone()
    else:
        uprns = ["null"]

    cur.close()

    return render_template(
        "usrn.html",
        street_type=record[0],
        usrn=record[1],
        usrn_geom=usrn_geom,
        uprn_geom=uprns[0],
        lat=lat,
        lon=lon,
        name="".join("\\n{}={}".format(k, v) for k, v in names.items()),
    )


@app.route("/authority/<authority>")
def authority(authority: str) -> str:
    authority_range = authority_map.get(authority)
    if not authority_range:
        return "Bad Authority"

    cur = conn.cursor()
    cur.execute(
        "SELECT street_type, usrn FROM usrn WHERE usrn > %s AND usrn < %s AND street_type != 'Numbered Street' AND street_type != 'Officially Described Street' ORDER BY usrn DESC LIMIT 500 OFFSET 0",
        (authority_range["USRN Start"], authority_range["USRN End"]),
    )
    records = cur.fetchall()
    cur.close()
    if not records:
        return ":( not found"

    return render_template("authority.html", usrns=records)
