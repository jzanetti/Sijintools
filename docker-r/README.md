## Build the demo:
```
docker build -t lambda-container-demo .
```

## Test the demo locally
- run the following commands in one terminal
   - `docker run -p 9000:8080 lambda-container-demo:latest "test.hello"` or 
   - `docker run -p 9000:8080 lambda-container-demo:latest "test.parity`

- test the function in another terminal, e.g.,
   - `curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"number": 6}'`


## Test the demo on AWS

- Create a reporsitory
   - `aws ecr create-repository --repository-name docker-r --image-scanning-configuration scanOnPush=true --region us-east-1`
- upload the image to ECR
   - tag: `docker tag lambda-container-demo 131344826993.dkr.ecr.us-east-1.amazonaws.com/docker-r:latest`
   - push: 
        `aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 131344826993.dkr.ecr.us-east-1.amazonaws.com`
        `docker push 131344826993.dkr.ecr.us-east-1.amazonaws.com/docker-r:latest`
        
        (Note that sometimes we you try to upload the image to ECR, it keep retrying, see the reference here: [link](https://stackoverflow.com/questions/70828205/pushing-an-image-to-ecr-getting-retrying-in-seconds))
- run lambda container
    - Click: _Lambda_ -> _Function_ -> _Create function_
    - Choose: _Container Image_
    - Set: _Function name_ and _Image URL_
    - Edit: _Image configuration_ -> _CMD_ (e.g., _test.parity_) -> we usually leave ENTRYPOINT/WORKDIR empty
    - Test: Create test, e.g., with input as `{'number': 5}`



## Some examples can be obtained at:
- https://mdneuzerling.com/post/r-on-aws-lambda-with-containers/
- https://stackoverflow.com/questions/71383387/trying-to-run-example-r-on-aws-lambda-with-containers
