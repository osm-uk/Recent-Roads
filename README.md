# Recent Roads

## Setup

### Load DB

PostGIS db
[OS Open USRN](https://osdatahub.os.uk/downloads/open/OpenUSRN)
[OSTN15](https://www.ordnancesurvey.co.uk/business-government/tools-support/os-net/for-developers)

```
$ ogr2ogr -sql "SELECT * FROM openUSRN" -s_srs "+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +units=m +no_defs +nadgrids=/home/cj/.local/share/QGIS/QGIS3/profiles/default/proj/OSTN15_NTv2_OSGBtoETRS.gsb" -t_srs EPSG:4326 -nln "osopenusrn_202401" -f "PostgreSQL" "postgresql://rr@localhost:5432/rr" Downloads/osopenusrn_202401_gpkg/osopenusrn_202401.gpkg
```

### Run

```
$ pipenv install
$ pipenv run python -m flask --app website run
```
