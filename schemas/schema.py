from pydantic import BaseModel, Field
from typing import Optional, List
import json

with open("./config.json", "r") as file:
    config = json.load(file)
SANDBOX_DOCKERFILE = config.get("SANDBOX_DOCKERFILE", "./default_dockerfile")

class CreateSessionRequest(BaseModel):
    lang: str = Field(..., description="The programming language for the session")
    image: str = Field(default="", description="Docker image to use")  # Default value for image, now required
    dockerfile: str = Field(default=SANDBOX_DOCKERFILE, description="Dockerfile to use")  # Default value for dockerfile, now required
    keep_template: bool = Field(True, description="Whether to keep the template")

class CodeExecutionRequest(BaseModel):
    code: str
    libraries: List[str] = Field(default="", description="library to pip install") 


class SessionResponse(BaseModel):
    output: str

class CopyFromRuntimeRequest(BaseModel):
    src_runtime_file: str = Field(..., description="Source file in the runtime to copy from")
    dest_local_path: str = Field(..., description="Local path to save the copied file")

class CopyToRuntimeRequest(BaseModel):
    dest_runtime_path: str = Field(default="./app", description="Destination path in the runtime")

class AddMountRequest(BaseModel):
    local_path: str = Field(..., description="Source path in the runtime to mount")
    runtime_path: str = Field(..., description="Destination path in the runtime for the mount")
    type: str = Field(default="bind", description="Type of the mount")