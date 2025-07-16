# USTC

## URL Design

### APIs

All following API endpoints are prefixed with `/api/v1/ustc/`.

- `GET /<model>/id/<id>`: Fetch a specific record by internal ID.
- `GET /<model>/jw-id/<id>`: Fetch a specific record by JW ID.
- `GET /<model>/list?<query_params>`: Fetch a list of records with optional query parameters.

### Pages

All following page endpoints are prefixed with `/ustc/`.

- `GET /`: Home page.
- `GET /<model>/`: List page for a specific model.
- `GET /<model>/id/<id>`: Detail page for a specific record by internal ID.
- `GET /<model>/jw-id/<id>`: Detail page for a specific record by JW ID.
