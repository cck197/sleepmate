docker run \
    --rm \
    --volume "$PWD/whoop_client":/out \
    docker.io/openapitools/openapi-generator-cli generate \
        --generator-name python \
        --input-spec 'https://api.prod.whoop.com/developer/doc/openapi.json' \
        --output '/out' \
        --package-name 'whoop_client' \
        --skip-validate-spec
