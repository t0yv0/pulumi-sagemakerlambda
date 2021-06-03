# pulumisagemakerlambda

Defines `SagemakerPredictorLambda` that provisions an AWS SageMaker
endpoint fronted by a custom Lambda function.

## Prerequisites

- Pulumi CLI
- Python 3.6+
- Go 1.15
- Node.js, Yarn (to build the Node SDK)
- .NET Code SDK (to build the .NET SDK)


## Build and Test

```bash

# Regenerate SDKs
make generate

# Build and install the provider and SDKs
make build
make install

# Test the example
$ cd examples/winequality

# setup venv against local Py SDK
$ source <(python local.py)

$ pulumi stack init test
$ pulumi config set aws:region us-east-1
$ pulumi up

# Follow instructions from `examples/winequality/README.md`.
```
