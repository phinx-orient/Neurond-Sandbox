from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_sandbox.docker import SandboxDockerSession
from typing import List, Optional, Dict
from fastapi import UploadFile, File
import os
import logging
from enum import Enum
import json


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allows all origins, you can specify a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Dictionary to store active sessions
active_sessions: Dict[str, SandboxDockerSession] = {}


with open("./config.json", "r") as file:
    config = json.load(file)
SANDBOX_DOCKERFILE = config.get("SANDBOX_DOCKERFILE")


class Language(str, Enum):
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    CPP = "cpp"
    GO = "go"
    RUBY = "ruby"


class CodeExecutionRequest(BaseModel):
    lang: str
    code: str
    libraries: Optional[List[str]] = None


class SessionResponse(BaseModel):
    output: str


@app.post("/create_session/")
async def create_session(
    session_id: str,
    lang: Language,  # Changed to use SupportedLanguage enum
    image: Optional[str] = None,
    dockerfile: Optional[str] = SANDBOX_DOCKERFILE,
    keep_template: bool = True,
):
    logger.info(f"Creating session: {session_id} with language: {lang}")
    if session_id in active_sessions:
        logger.error("Session ID already exists.")
        raise HTTPException(status_code=400, detail="Session ID already exists.")

    try:
        session = SandboxDockerSession(
            lang=lang,
            image=image,
            dockerfile=dockerfile,
            keep_template=keep_template,
        )
        session.open()
        active_sessions[session_id] = session
        logger.info(f"Session created successfully: {session_id}")
        return {"message": "Session created successfully.", "session_id": session_id}
    except ValueError as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/sessions/")
async def get_sessions():
    logger.info("Retrieving active sessions.")
    return {"active_sessions": list(active_sessions.keys())}


@app.get("/session_metadata/{session_id}/")
async def get_session_metadata(session_id: str):
    logger.info(f"Retrieving metadata for session: {session_id}")
    session = active_sessions.get(session_id)
    if not session:
        logger.error("Session not found.")
        raise HTTPException(status_code=404, detail="Session not found.")

    # Assuming the session object has a method to get metadata
    metadata = {
        "lang": session.lang,
        "dockerfile": session.dockerfile,
        "keep_template": session.keep_template,
    }
    logger.info("Session metadata retrieved successfully.")
    return {"session_id": session_id, "metadata": metadata}


@app.post("/run_code/{session_id}/", response_model=SessionResponse)
async def run_code(session_id: str, request: CodeExecutionRequest):
    logger.info(f"Running code in session: {session_id}")
    session = active_sessions.get(session_id)
    if not session:
        logger.error("Session not found.")
        raise HTTPException(status_code=404, detail="Session not found.")

    try:
        output = session.run(request.code, libraries=request.libraries)
        logger.info("Code executed successfully.")
        return SessionResponse(output=output.text)
    except RuntimeError as e:
        logger.error(f"Runtime error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/close_session/{session_id}/")
async def close_session(session_id: str):
    logger.info(f"Closing session: {session_id}")
    session = active_sessions.pop(session_id, None)
    if not session:
        logger.error("Session not found.")
        raise HTTPException(status_code=404, detail="Session not found.")

    try:
        session.close()
        logger.info("Session closed successfully.")
        return {"message": "Session closed successfully."}
    except RuntimeError as e:
        logger.error(f"Runtime error while closing session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/copy_from_runtime/{session_id}/")
async def copy_from_runtime(session_id: str, src: str, dest: str = "./sandbox"):
    logger.info(f"Copying from runtime in session: {session_id} from {src} to {dest}")
    session = active_sessions.get(session_id)
    if not session:
        logger.error("Session not found.")
        raise HTTPException(status_code=404, detail="Session not found.")

    try:
        session.copy_from_runtime(src, dest)
        logger.info("File copied successfully.")
        return {"message": f"File copied from {src} to {dest} successfully."}
    except RuntimeError as e:
        logger.error(f"Runtime error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/copy_to_runtime/{session_id}/")
async def copy_to_runtime(
    session_id: str, src: UploadFile = File(...), dest: str = "./sandbox"
):
    logger.info(
        f"Copying to runtime in session: {session_id} from {src.filename} to {dest}"
    )
    session = active_sessions.get(session_id)
    if not session:
        logger.error("Session not found.")
        raise HTTPException(status_code=404, detail="Session not found.")

    temp_file_path = f"/tmp/{src.filename}"
    try:
        # Save the uploaded file to a temporary location
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await src.read())

        session.copy_to_runtime(temp_file_path, dest)
        logger.info("File copied to runtime successfully.")
        return {"message": f"File copied to runtime at {dest} successfully."}
    except RuntimeError as e:
        logger.error(f"Runtime error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Clean up the temporary file if it exists
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Temporary file {temp_file_path} removed.")


@app.post("/add_mount/{session_id}/")
async def add_mount(session_id: str, source: str, target: str, type: str = "bind"):
    logger.info(f"Adding mount in session: {session_id} from {source} to {target}")
    session = active_sessions.get(session_id)
    if not session:
        logger.error("Session not found.")
        raise HTTPException(status_code=404, detail="Session not found.")

    try:
        session.add_mount(source, target, type)
        logger.info("Mount added successfully.")
        return {"message": "Mount added successfully."}
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
