# Use the official Golang image to create a build artifact.
FROM golang:1.18

# Set the Current Working Directory inside the container
WORKDIR /app

# Copy the main.go file
COPY main.go .

# Initialize a new module and tidy to install dependencies
RUN go mod init example.com/myapp && go mod tidy

# Build the Go app
RUN go build -o main .

# Command to run the executable
CMD ["./main"]
