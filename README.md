### AUTO-FEED-DEFECTDOJO

Ejemplo básico (* en desarrollo) de web-service para automatizar la ejecución de herramientas preconfiguradas e importación de resultados en DefectDojo.
Herramientas configuradas al momento (de acuerdo a nombres de importación en DefectDojo): "Nmap Scan", "Nikto Scan", "Wapiti Scan", "SSLyze 3 Scan (JSON)", "DrHeader JSON Importer", "ZAP Scan", "OpenVAS CSV".

```

git clone https://github.com/arielmaiorano/auto-feed-defectdojo && cd auto-feed-defectdojo
docker build -t afdd .
docker run -e DEFECT_DOJO_URL="<url>" -e DEFECT_DOJO_TOKEN="<token defectdojo>" -e DEFECT_DOJO_ENGAGEMENT_ID="<id de engagement>" -e GVM_HOSTNAME="<hostname>" -e GVM_USERNAME="<username>" -e GVM_PASSWORD="<passoword>" -d -p 9090:9090 afdd

```

Luego puede accederse a la documentación autogenerada de la API en http://127.0.0.1:9090/docs para probar el manejo de tareas.

#### DefectDojo

De acuerdo a lo indicado en https://github.com/DefectDojo/django-DefectDojo#quick-start

```

git clone https://github.com/DefectDojo/django-DefectDojo
cd django-DefectDojo
# building
docker-compose build
# running
docker-compose up
# obtain admin credentials
docker-compose logs initializer | grep "Admin password:"

```

#### GVM/OpenVAS

De acuerdo a https://securecompliance.gitbook.io/projects/openvas-greenbone-deployment-full-guide/deploying-greenbone-gvm-gsa-with-openvas pero habilitando ssh y mapeando el puerto 9390

```

docker run --detach --publish 8088:9392 --publish 9390:9390 --publish 5432:5432 --publish 2222:22 --env DB_PASSWORD="<password>" --env PASSWORD="<password>" --env SSHD="true" --volume gvm-data:/data --name gvm securecompliance/gvm

```
