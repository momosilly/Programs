FROM python:trixie

# Stel de werkmap in
WORKDIR /app

# Kopieer de requirements file en installeer de afhankelijkheden
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

