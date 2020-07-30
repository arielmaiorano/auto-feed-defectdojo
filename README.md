### AUTO-FEED-DEFECTDOJO

Ejemplo/prueba básica de web-service implementado con FastAPI para la ejecución de herramientas preconfiguradas e importación de resultados en DefectDojo (ejemplos con nmap y nikto).

```

git clone <este repo> && cd auto-feed-defectdojo
docker build -t afdd .
docker run -e DEFECT_DOJO_URL="<url>" -e DEFECT_DOJO_TOKEN="<token defectdojo>" -e DEFECT_DOJO_ENGAGEMENT_ID="<id de engagement>" -d -p 9090:9090 afdd

```

Luego puede accederse a la documentación de la API en http://127.0.0.1:9090/docs para probar el manejo de tareas.

