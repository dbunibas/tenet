db = db.getSiblingDB('tenet');

db.createCollection('users');

db.users.insertOne(
  {
    "username": "admin",
    "password": "0dc1e407b82b610ec695936497b694dd"
  }
);