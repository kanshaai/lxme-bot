FROM python:3.10-slim
WORKDIR /app

ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ARG SERPER_API_KEY
ENV SERPER_API_KEY=${SERPER_API_KEY}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "main.py"]