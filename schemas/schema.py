from pydantic import BaseModel, Field
from typing import Optional, List
import json

with open("./config.json", "r") as file:
    config = json.load(file)
SANDBOX_DOCKERFILE = config.get("SANDBOX_DOCKERFILE", "./default_dockerfile")

class CreateSessionRequest(BaseModel):
    lang: str = Field(..., description="The programming language for the session")
    image: Optional[str] = Field(None, description="Optional Docker image")
    dockerfile: Optional[str] = Field(SANDBOX_DOCKERFILE, description="Dockerfile to use")
    keep_template: bool = Field(True, description="Whether to keep the template")

class CodeExecutionRequest(BaseModel):
    lang: str
    code: str
    libraries: Optional[List[str]] = None


class SessionResponse(BaseModel):
    output: str