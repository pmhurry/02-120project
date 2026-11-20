"""Vercel ASGI entry point for the existing Streamlit interface."""
from pathlib import Path

from fastapi import FastAPI
import streamlit as st

streamlit_app = st.App(Path(__file__).with_name("app.py"))
app = FastAPI(lifespan=streamlit_app.lifespan(), docs_url=None, redoc_url=None,
              openapi_url=None)
app.mount("/", streamlit_app)
