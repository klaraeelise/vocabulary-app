# syntax=docker/dockerfile:1
FROM golang:1.23-alpine

WORKDIR /app
COPY . .

# Compile the Go service
RUN go mod tidy && go build -o server .

# Run the server
CMD ["./server"]
