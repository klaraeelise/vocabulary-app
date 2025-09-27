# ---- build stage ----
FROM golang:1.24 AS builder
WORKDIR /app

# Enable new toolchain resolver just in case
ENV GOTOOLCHAIN=auto

# Cache modules
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest and build
COPY . .
# If your entrypoint is main.go at repo root:
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o server .

# ---- runtime stage (tiny, no shell) ----
FROM gcr.io/distroless/static-debian12
WORKDIR /app
COPY --from=builder /app/server /app/server
EXPOSE 8080
USER nonroot:nonroot
ENTRYPOINT ["/app/server"]
