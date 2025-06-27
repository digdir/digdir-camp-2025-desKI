from app.services.log_query_service import LogQueryService

url = "http://loki-api:3100/loki/api/v1/query_range"
params = {
    "query": '{service_name=~"sample-app"} |= "traceID=a1b2c3d4-e5f6-7890-abcd-ef1234567890"'
}

#response = requests.get(url)
#print(response.status_code)

logQueryService = LogQueryService(api_base_url=url)

print(logQueryService.get_logs(params))