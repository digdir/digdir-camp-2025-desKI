from fastapi import FastAPI

#from app.api.routes import router

#app = FastAPI()
#app.include_router(router, prefix='/chat')
from app.services.log_query_service import LogQueryService

logQueryService = LogQueryService()

print(logQueryService.get_logs('{service_name=~"sample-app"} |= "traceID=a1b2c3d4-e5f6-7890-abcd-ef1234567890"'))