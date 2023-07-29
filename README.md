# LargeFileTransfer

Run the app and use Insomnia/Postman/cURL/etc to send a multipart form with `file: <your file here>`. The app defaults to running on `localhost:8080`.

The app will return a link that can be used to access the uploaded file again.

Old files (files that have not been accessed in a day or more) will be cleaned up hourly.