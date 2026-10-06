# Architecture

DataPulse is designed like a practical data engineering reliability layer.

## Components

### Source Data

The source can be:

- generated sample CSV files
- manually uploaded CSV files
- files dropped into `data/incoming`

### Normalization Layer

The normalizer maps common source aliases to the expected data contract.

Examples:

- `price` -> `amount`
- `qty` -> `quantity`
- `order date` -> `order_ts`
- `payment` -> `payment_method`

### Validation Layer

The validator checks:

- required columns
- required values
- numeric amount
- positive amount
- integer quantity
- positive quantity
- valid timestamp
- allowed country
- allowed payment method
- duplicate order ID

### Storage Layer

PostgreSQL stores:

- `pipeline_runs`
- `clean_orders`
- `quarantined_records`
- `quality_checks`
- `repair_suggestions`

### Repair Layer

The repair engine groups validation issues by type and generates practical suggestions. This is intentionally deterministic and auditable, which is better than pretending to call an external AI model without one.

### Serving Layer

FastAPI exposes the pipeline data through REST endpoints.

### Dashboard Layer

Streamlit visualizes:

- latest pipeline runs
- quality score trend
- failed checks
- repair suggestions
- quarantined records
