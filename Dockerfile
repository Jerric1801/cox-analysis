FROM python:3.11-slim-buster

WORKDIR /app

COPY app/pyproject.toml app/poetry.lock ./
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry lock --no-update  
RUN poetry install --no-interaction --no-ansi

COPY app/ .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Expose port 3001
EXPOSE 3001

# Run the Flask app on port 3001
CMD ["flask", "run", "--host=0.0.0.0", "--port=3001", "--debug"]

