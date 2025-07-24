FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY process_pdfs.py .

CMD ["python", "process_pdfs.py"]
