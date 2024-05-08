import database as db
import os

# delete the database file
os.remove("colonoscopy_management.db")

# delete images inside output/raw and output/segmented
os.system("rm -rf output/raw/*")
os.system("rm -rf output/segmented/*")

db.init_database()

db.insert_Doctor("Dr. Abdelrhman Nile", "Gastroenterologist")
db.insert_EndoscopeDevice("Olympus Exera III", "Room 1")
db.insert_DetectionModel("Yolo", "v8")
db.insert_SegmentationModel("DE-ColonSegNet", "v1")
db.insert_Patient("Ahmed", "2000-01-01", "Male")
