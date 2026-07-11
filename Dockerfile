FROM python:3.11-slim

WORKDIR /app

# 后端依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 后端代码
COPY backend/ .

# 前端构建产物
COPY frontend/dist/ ./static/

EXPOSE 8000

ENV ENVIRONMENT="production"
# SECRET_KEY、ADMIN_USERNAME、ADMIN_PASSWORD、DEEPSEEK_API_KEY 必须由部署平台注入。

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
