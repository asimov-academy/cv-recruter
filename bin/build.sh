#!/bin/sh

poetry run streamlit run analyser/app.py --server.address 0.0.0.0 --server.port 8585
