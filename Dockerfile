FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install git-lfs -y &&  \
    git lfs install &&  \
    git clone https://huggingface.co/openai/whisper-small /tmp/model &&  \
    rm -rf /tmp/model/.git

COPY requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

FROM python:3.12-slim

COPY --from=builder /root/.local /root/.local
COPY --from=builder /tmp/model /tmp/model
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app
COPY . /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]