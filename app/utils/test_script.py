from app.services.log_query_service import LogQueryService

# Define the API base URL
url = 'http://loki-api:3100/loki/api/v1/query_range'

# Define query parameters
params = {
    'query': '{service_name=~"sample-app"} |= "traceID=a1b2c3d4-e5f6-7890-abcd-ef1234567890"'
}

# Optional: test the URL directly with requests
# response = requests.get(url, params=params)
# print(response.status_code)

# Create an instance of LogQueryService
logQueryService = LogQueryService(api_base_url=url)

# Fetch and print logs
print(logQueryService.get_logs(params))
