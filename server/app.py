"""
server/app.py — Multi-mode deployment entry point for Medical AI Doctor OpenEnv.
This module re-exports the FastAPI app from main.py so openenv-core can locate it
via the [project.scripts] entry point: medical-ai-doctor-server = server.app:app
"""
from main import app

__all__ = ["app"]