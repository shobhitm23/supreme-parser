from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import re, pytz, logging, os.path
app = FastAPI()

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Create a file handler to log errors
file_handler = logging.FileHandler("error.log")
file_handler.setLevel(logging.ERROR)

# Create a formatter and add it to the file handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Regex to match iso8601 UTC format
date_time_pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
TESTFILEPATH = '/app/test-files'

@app.post("/")
async def parse_file(request: Request):
    try:
        data = await request.json()
        filename = data["filename"]
        from_time = data["from"]
        to_time = data["to"]
        
        # Check if file has .txt extension
        if not filename.endswith(".txt"):
            logger.error("Invalid file format. File must be of .txt format")
            return JSONResponse(content={"error": "Invalid file format. File must be of .txt format"}, status_code=415)

        # Check if from and to timestamps are in iso8601 UTC format
        # Possible iso UTC timestamps can be
        # YYYY-MM-DDThh:mm:ssZ 
        # YYYY-MM-DDThh:mm:ss+00:00
        # But we're only handling one format at the moment - YYYY-MM-DDThh:mm:ssZ
        if not date_time_pattern.match(from_time) or not date_time_pattern.match(to_time):
            logger.error("Invalid timestamp format. Timestamps must be in iso8601 UTC Format - YYYY-MM-DDThh:mm:ssZ")
            return JSONResponse(content={"error":"Invalid timestamp format. Timestamp must be in iso8601 UTC Format - YYYY-MM-DDThh:mm:ssZ"}, status_code=400)

        # Check if user entered invalid time example - 2000-01-01T45:12:12Z
        try:
            from_time = datetime.fromisoformat(from_time[:-1] + "+00:00")
            to_time  = datetime.fromisoformat(to_time[:-1] + "+00:00")
        
        except ValueError:
            logger.error("Invalid input. Please ensure the time entered is valid")
            return JSONResponse(content={"error": "Invalid input. Please ensure the time entered is valid"}, status_code=400)

        if from_time > to_time:
            logger.error("Invalid input. Please ensure 'from' input is earlier than 'to' input")
            return JSONResponse(content={"error":"Invalid input. Please ensure 'from' input is earlier than 'to' input"}, status_code=400)

        # Check if file requested by user exists and is not empty
        try:
            if not os.path.isfile(os.path.join(TESTFILEPATH, filename)):
                raise FileNotFoundError
        
            elif not os.path.getsize(os.path.join(TESTFILEPATH, filename)):
                raise ValueError
        
        except FileNotFoundError as e:
            logger.error(f"File Not Found error: '/app/test-files/{filename}'")
            return JSONResponse(content={"error": f"File Not Found error: '/app/test-files/{filename}'"}, status_code=404)
            
        except ValueError as e:
            logger.error("File is empty")
            return JSONResponse(content={"error": "File is empty"}, status_code=204)

        results = []

        for obj in lines_filter(filename, from_time, to_time):
            if obj == {}:
                results.clear()
                break; 
            results.append(obj)

        # Sort results by date and return response
        results.sort(key=lambda x: x["eventTime"])
        return JSONResponse(content=results or [], media_type="application/json", status_code=200)
    
    except ValueError:
        raise
        
def lines_filter(filename, from_time, to_time):

    result = []
    line_number = 0
    with open(os.path.join(TESTFILEPATH, filename), 'r', encoding='utf-8-sig') as infile:
        for line in infile:
            line_number += 1
            try:
                line = line.rstrip()
                date, email, session_id = line.strip().split(" ")

                # Covert to datetime object
                date_time = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                
            except ValueError:
                logger.error('Error on line {}: {}'.format(line_number, line))
                yield {}
            
            else:
                # Create a timezone object for UTC
                utc_tz = pytz.timezone("UTC")
                # Localize the datetime object with the UTC timezone
                date_time = utc_tz.localize(date_time)
                # Compare record time with input to append to result
                if from_time <= date_time <= to_time:
                    yield {
                        "eventTime": date,
                        "email": email,
                        "sessionId": session_id
                    }
                
    return result