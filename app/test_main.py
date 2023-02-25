from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)


# Test to check if app responds with a 200 status code for valid input
def test_valid_inputs():
    from_time = "2000-01-01T00:15:30Z"
    to_time = "2000-01-21T13:15:30Z"
    filename = "sample1.txt"

    response = client.post(
        "/", json={"filename": filename, "from": from_time, "to": to_time}
    )

    assert response.status_code == 200


# Test to check response code for an empty file
def test_empty_file():
    from_time = "2000-01-01T00:00:00Z"
    to_time = "2000-01-02T00:00:00Z"
    filename = "sample5.txt"

    response = client.post(
        "/", json={"filename": filename, "from": from_time, "to": to_time}
    )
    assert response.status_code == 204


# Test to check response for an invalid file format
def test_invalid_file_format():
    from_time = "2022-01-01T00:00:00Z"
    to_time = "2022-01-02T00:00:00Z"
    filename = "test_file.jpg"

    response = client.post(
        "/", json={"filename": filename, "from": from_time, "to": to_time}
    )
    assert response.status_code == 415
    assert response.json() == {
        "error": "Invalid file format. File must be of .txt format"
    }


# Test to check response for invalid timestamps format
def test_invalid_timestamps_format():
    from_time = "2022-01-01T00:00:0frfgrgZ"
    to_time = "2022-01-02T00:00:0grgrgZ"
    filename = "sample1.txt"

    response = client.post(
        "/", json={"filename": filename, "from": from_time, "to": to_time}
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": "Invalid timestamp format. Timestamp must be in iso8601 UTC Format - YYYY-MM-DDThh:mm:ssZ"
    }


# Tes to check response for invalid datetime - example 2000-01-01T27:15:30Z
def test_invalid_timestamp():
    from_time = "2000-01-01T27:15:30Z"
    to_time = "2000-01-04T13:15:30Z"
    filename = "sample1.txt"

    response = client.post(
        "/", json={"filename": filename, "from": from_time, "to": to_time}
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": "Invalid input. Please ensure the time entered is valid"
    }


# Test to check response when input file is not found
def test_file_not_found():
    response = client.post(
        "/",
        json={
            "filename": "non_existent_file.txt",
            "from": "2022-10-22T00:00:00Z",
            "to": "2022-10-23T00:00:00Z",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": "File Not Found error: '/app/test-files/non_existent_file.txt'"
    }
