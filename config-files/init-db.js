db = db.getSiblingDB("test");
db.test_tb.drop();

db.test_tb.insertMany([
    {
        "creation_date": "Tue, 25 Jan 2022 00:00:00 GMT",
        "longurl": "http://www.google.com",
        "type": "http://hWvGLux",
        "userId": 100000
    },
]);