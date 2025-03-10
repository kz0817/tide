How to build a development container
===

```
docker build -t tide-dev .
```

How to run a development container
===

On the top directory of this project, run the following command.
```
docker run -it -v $(pwd):/share -w /share tide-dev bash
```
