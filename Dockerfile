FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
#1. FROM python:3.11-slim — Start from an official Python image (slim = small size)
 #2. WORKDIR /app — Set the working directory inside the container
 #3. COPY requirements.txt . — Copy the dependency list first (this is a caching optimization)
 #4. RUN pip install — Install all Python packages inside the container
 #5. COPY . . — Copy the actual application code
 #6. EXPOSE 8080 — Document that the app uses port 8080
 #7. CMD [uvicorn...] — The command that runs when the container starts