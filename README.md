# Recent Roads

## Setup

### Load DB

PostGIS db
[OS Open USRN](https://osdatahub.os.uk/downloads/open/OpenUSRN)
[OSTN15](https://www.ordnancesurvey.co.uk/business-government/tools-support/os-net/for-developers)

```bash
export DATABASE_URI="postgresql://user:password@host/db"

ogr2ogr -sql "SELECT * FROM openUSRN" -s_srs "+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +units=m +no_defs +nadgrids=/home/cj/.local/share/QGIS/QGIS3/profiles/default/proj/OSTN15_NTv2_OSGBtoETRS.gsb" -t_srs EPSG:4326 -nln "usrn" -f "PostgreSQL" $DATABASE_URI '/vsizip//home/cj/Documents/Downloads/osopenusrn_202511_gpkg.zip/osopenusrn_202511.gpkg' -overwrite
ogr2ogr -sql "SELECT * FROM Road_TOID_Street_USRN_10" -nln "usrn2toid" -f "PostgreSQL" $DATABASE_URI Road_TOID_Street_USRN_10.csv
ogr2ogr -sql "SELECT * FROM road_link" -nln "toid2name" -f "PostgreSQL" $DATABASE_URI oproad_gb.gpkg
ogr2ogr -sql "SELECT UPRN FROM osopenuprn_202509" -oo X_POSSIBLE_NAMES=longitude -oo Y_POSSIBLE_NAMES=latitude -oo KEEP_GEOM_COLUMNS=NO -nln "uprn" -f "PostgreSQL" $DATABASE_URI osopenuprn_202509.csv
ogr2ogr -sql "SELECT * FROM BLPU_UPRN_Street_USRN_11" -nln "uprn2usrn" -f "PostgreSQL" $DATABASE_URI BLPU_UPRN_Street_USRN_11.csv
ogr2ogr -oo X_POSSIBLE_NAMES=lon -oo Y_POSSIBLE_NAMES=lat -oo KEEP_GEOM_COLUMNS=NO -nln "os_open_apt" -f "PostgreSQL" $DATABASE_URI os-open-apt-NSUL-2025-09.csv
```

### Run

```bash
pipenv install
pipenv run python -m flask --app website run
```
