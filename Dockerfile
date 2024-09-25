# BUILDER
FROM python:3.9.20-alpine as builder

WORKDIR /usr/src/app

# Activate virtualenv
RUN python -m venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and build with pip
COPY requirements.txt ./
RUN pip install -r requirements.txt



# RUNTIME
FROM python:3.9.20-alpine as runtime

WORKDIR /usr/src/app

# Copy compiled venv from builder
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy health check script
#COPY healthcheck.py .
#HEALTHCHECK CMD ["python", "./healthcheck.py"]

# Copy script over and run
COPY fusion.py .
CMD [ "python", "./fusion.py" ]
