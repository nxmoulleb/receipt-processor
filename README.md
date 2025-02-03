# receipt-processor
Hi, my name is Nicholas Moulle-Berteaux. Thank you for taking the time to review my application to Fetch!

My solution to this problem is built using Python. I am using Flask to create my endpoints. 

The server I made is open on `0.0.0.0:8080`. Once the Docker container is run, you will be able to access the following endpoints:
* `http://0.0.0.0:8080/receipts/<id>/points`
* `http://0.0.0.0:8080/receipts/process`

## Running the Docker Container
1. Run `docker build -t receipts-server .`. This will create an image named `receipts-server`.

2. Run `docker run --name receipts-server -p 8080:8080 receipts-server`. This will create a container named `receipts-server`.

3. Have fun! Hopefully you dont break anything too badly.