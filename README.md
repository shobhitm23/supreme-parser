Rokt Parser
===

Please fill out your readme here.

The goal of the Take Home Assessment was to build a Web based parser using Docker.
Idea was to parse input text files and provide a response based on the date ranges provided by the User.

To build the web based application, I decided to use FASTAPI Framework - a high performance web framework for building APIs using Python

This is a sample basic input that should provide you with a response.

## Request
```JSON
{
    "filename": "sample1.txt",
    "from": "2000-01-05T13:15:30Z",
    "to": "2000-01-06T13:15:30Z"
}
```

## Response

```JSON
[
    {
        "eventTime": "2000-01-05T13:15:45Z",
        "email": "bryana_olson@heidenreich.uk",
        "sessionId": "d15eb4ec-32cd-4267-b1c1-8fe7b4920539"
    },
    {
        "eventTime": "2000-01-05T13:17:19Z",
        "email": "ola@wizahuel.ca",
        "sessionId": "b91bf764-2a1a-41c6-9d7b-981ec62455be"
    },
    {
        "eventTime": "2000-01-05T13:18:03Z",
        "email": "griffin.pacocha@doyle.co.uk",
        "sessionId": "7d5acdb4-4536-4e9e-85e7-143060c5ded8"
    }
]
```

## Proposed Solution

- **Parse and Validate Incoming Requests**

  - I have implemented a series of checks to ensure that the provided file is in the correct format (.txt)
  - provided dates are in the correct format (ISO8601 UTC)
  - As per https://en.wikipedia.org/wiki/ISO_8601, both **YYYY-MM-DDThh:mm:ssZ** and **YYY-MM-DDThh:mm:ss+00:00** are 
    valid formats but currently the instructions require us to support only the former format
  - 'from' date is earlier than the 'to' date
  - the input files exist in our designated directory `/app/test-files` and are not empty

- **Load data and filter results**


To improve the performance and robustness of the code, I have researched and considered multiple options for loading and filtering large input files. Some possible methods - 

 - using generators in python
 - use `jsonlines` or similar libraries to write the data to the response in a streaming fashion, 
 this will allow to write data as soon as it's available

Generator functions act as an iterator; they use `yield instead of return` which allows us to process each filtered match 
one at a time and not all at once in memory.

  - Initially my approach was to filter and respond with matches only from valid data and **skip lines with invalid data** 
  whether it be invalid date, missing spaces or invalid format to ensure consistency and accuracy
  - Additonally, I could log errors and keep track of input data that wasn't able to be parsed.

> If the input is invalid, or there are no valid entries, your application should return a 200 HTTP status response code, 
a content-type of application/json, and the following response body: `[]`
 
As per this requirement, my solution is designed to only return filtered responses whent the entire file comprises of valid data. If there is any invalid input such as invalid date format, missing spaces - the code will respond with an empty body `[]` along with a 200 status code

Implementing generator objects didn't make much of a difference when it came to performance. I believe appending the results before sending the response could be a potential bottleneck when it comes to performace for larger input files.

There might be a way to directly stream JSON responses without compiling it into a list, but we do require to sort the list based on eventTime parameter of each filtered response.

However, to improve responses we could potentially consider using a DB with some form of caching. Caching mechanisms can allow retrieving past search results quickly for the users.

- **Logging, Debuging and Status Codes**

    - Utlized logging module to log errors into `error.log` within the `/app` directory
    - Incorporated appropriate status codes for any input responses to ensure proper error handling 

- **Testing**

I have used the pytest library to add some test cases to perform input validations, check for invalid request formats and ensure the application responds with appropriate status code and responses.

- **Any possible improvements**

    - Add test cases for performance testing and load testing
    - Improve bottlenecks within the solution - possibly implement a streaming solution or some form of caching