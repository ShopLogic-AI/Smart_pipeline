FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy the dataset inside the image
COPY data/products_data.csv /app/data/products_data.csv

# Install necessary libraries
RUN pip install pandas scikit-learn

# Default command (you can ignore this in pipelines)
CMD ["bash"]
