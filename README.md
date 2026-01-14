# EdDSA API Implementation

> Created for research purposes only.

## Running Environment

### Generate Key

Universal setup. For testing 2 accounts, run twice:

```bash
python utils.py keygen
```

### Signing Key & Request Body

Testing airtime recharge:

```bash
python utils.py sign <PRIVATE_KEY_ALPHA> alpha-group
python utils.py sign <PRIVATE_KEY_ALPHA> beta-group
```

Testing inquiry:

```bash
python utils.py inquiry <PRIVATE_KEY_ALPHA> beta-group
python utils.py inquiry <PRIVATE_KEY_BETA> beta-group
```

### Environment Configuration

Create a `.env` file with the mock public keys:

```env
MOCK_PUBLIC_KEYS='{"alpha-group": "gJPu9l8zG8g5HRkBR9g0/zGah0Cwnu1JBrOnL9oAcW8=", "beta-group": "v3S6X9v2p...[key_lain]..."}'
```

### Docker Setup

Build and run the application using Docker:

```bash
docker build -t airtime-api .
docker run -p 8000:8000 --env-file .env airtime-api
```
