# Use AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies for building packages
RUN yum update -y && \
    yum install -y gcc g++ && \
    yum clean all

# Copy requirements first for better Docker layer caching
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/

# Set the command to run the Lambda handler
CMD ["lambda_handler.handler"]