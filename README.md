# WomSoft Server

This project exposes a small FastAPI service used for demo purposes. Users are stored in a SQLite database and JWT is used for authentication.

## Roles

Users now include a `role` field. Supported roles are:

- `admin`
- `doctor`
- `labtech`
- regular `user`

Administrators can access the admin endpoints. Doctors can create test orders which are later fulfilled by lab technicians.

## Test Order Workflow

1. A doctor calls `POST /api/orders/` with the patient name to create a new order.
2. A lab technician calls `POST /api/orders/{order_id}/fulfill` with diagnostic values to generate results and mark the order as fulfilled.
3. Orders can be listed with `GET /api/orders/`.

Run the tests with:

```bash
pytest -q
```
