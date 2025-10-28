

>docker run --name backend -p 8000:80 antropy


docker start -a backend

docker ps -a
docker stop backend
dockert restart backend
docker logs -f backend

---
####  pre-commit
code checks: using pre-commit for formatting with ruff and other pre commit hooks
`uv tool install pre-commit --with pre-commit-uv`

(configure pre-commit and Ruff)[https://stefaniemolin.com/articles/devx/pre-commit/setup-guide/]
ruff as formatter

#### pytest-pre-commit
for running tests, added to .pre-commit-config.yaml

### Tests
`uv add --dev pytest`
