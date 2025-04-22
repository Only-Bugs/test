# syntax=docker/dockerfile:1

####### builder stage: compile wheels #######
FROM python:3.10-slim AS builder

# install compilers & headers for any native deps
RUN apt-get update && apt-get install --no-install-recommends -y \
      gcc libffi-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY app/requirements.txt .

# build all wheels into /build/wheels
RUN pip install --upgrade pip wheel \
 && pip wheel --no-deps --wheel-dir=./wheels -r requirements.txt

####### runtime stage: install + ship #######
FROM python:3.10-slim AS runtime

# OpenCV runtime dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
      libgl1 libglib2.0-0 libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# install from our pre‑built wheels
COPY --from=builder /build/wheels /wheels
COPY app/requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt \
 && rm -rf /wheels

# copy your application code
COPY app ./app

# expose your FASTAPI port
EXPOSE 8000

# run as root (no USER line)
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
