# Short URL Service

A RESTful URL shortening service built with FastAPI. It provides APIs to create short URLs and redirect users to the original URLs, with expiration and rate limiting.

## Features
- Create short URLs for any valid HTTP/HTTPS link
- Redirect using the short URL
- Expiration policy (default: 30 days)
- Rate limiting (10 requests per minute per IP)
- Input validation and robust error handling
- Packaged as a Docker container

## API Documentation

### 1. Create Short URL
- **Endpoint:** `POST /api/shorten`
- **Request Body:**
  ```json
  {
    "original_url": "https://example.com"
  }
  ```
- **Response:**
  - **Success:**
    ```json
    {
      "short_url": "http://localhost:8000/abc123",
      "expiration_date": "2024-07-10T12:00:00.000000",
      "success": true,
      "reason": null
    }
    ```
  - **Failure (invalid URL):**
    ```json
    {
      "short_url": null,
      "expiration_date": null,
      "success": false,
      "reason": "Invalid URL"
    }
    ```
  - **Failure (rate limit):**
    ```json
    {
      "success": false,
      "reason": "Rate limit exceeded. Try again later."
    }
    ```

### 2. Redirect Using Short URL
- **Endpoint:** `GET /{short_code}`
- **Behavior:**
  - Redirects to the original URL if valid and not expired
  - **404** if not found
  - **410** if expired

## Running with Docker

### 1. Build the Docker image
```sh
docker build -t yourdockerhubusername/short-url-service .
```

### 2. Run the container
```sh
docker run -d -p 8000:8000 --name short-url-service yourdockerhubusername/short-url-service
```

- The service will be available at `http://localhost:8000`

### 3. Example Usage
#### Create a short URL
```sh
curl -X POST "http://localhost:8000/api/shorten" -H "Content-Type: application/json" -d '{"original_url": "https://example.com"}'
```

#### Redirect
Open the returned `short_url` in your browser.

## Configuration
- No additional configuration is required.
- Data is stored in a local SQLite file (`shorturl.db`).

## Notes
- Replace `yourdockerhubusername` with your Docker Hub username when building/pushing the image.
- To push to Docker Hub:
  ```sh
  docker login
  docker tag short-url-service yourdockerhubusername/short-url-service
  docker push yourdockerhubusername/short-url-service
  ```

## License
MIT 