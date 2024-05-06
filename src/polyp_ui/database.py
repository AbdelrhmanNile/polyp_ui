import sqlite3


def init_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS Doctor (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name STRING,
            Specialization STRING
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS Patient (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name STRING,
            DateOfBirth DATE,
            Gender STRING
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS EndoscopeDevice (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Model STRING,
            Location STRING
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS ColonoscopySession (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DoctorID INTEGER,
            PatientID INTEGER,
            DeviceID INTEGER,
            SessionDateTime DATETIME,
            FOREIGN KEY (DoctorID) REFERENCES Doctor(ID),
            FOREIGN KEY (PatientID) REFERENCES Patient(ID),
            FOREIGN KEY (DeviceID) REFERENCES EndoscopeDevice(ID)
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS ColonoscopyImage (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            SessionID INTEGER,
            ImagePath STRING,
            FOREIGN KEY (SessionID) REFERENCES ColonoscopySession(ID)
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS DetectionModel (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ModelName STRING,
            ModelVersion STRING
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS DetectedPolyps (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ImageID INTEGER,
            DetectionModelID INTEGER,
            Count INTEGER,
            FOREIGN KEY (ImageID) REFERENCES ColonoscopyImage(ID),
            FOREIGN KEY (DetectionModelID) REFERENCES DetectionModel(ID)
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS SegmentationModel (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ModelName STRING,
            ModelVersion STRING
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS SegmentationOutput (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PolypID INTEGER,
            SegmentationModelID INTEGER,
            ImagePath STRING,
            FOREIGN KEY (PolypID) REFERENCES DetectedPolyps(ID),
            FOREIGN KEY (SegmentationModelID) REFERENCES SegmentationModel(ID)
        )
        """
    )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Database and tables created successfully.")


# To initialize the database, call init_database()


def insert_Doctor(Name, Specialization):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO Doctor (Name, Specialization)
        VALUES (?, ?)
        """,
        (Name, Specialization),
    )

    conn.commit()
    conn.close()


def insert_Patient(Name, DateOfBirth, Gender):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO Patient ( Name, DateOfBirth, Gender)
        VALUES ( ?, ?, ?)
        """,
        (Name, DateOfBirth, Gender),
    )

    conn.commit()
    conn.close()


def insert_EndoscopeDevice(Model, Location):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO EndoscopeDevice ( Model, Location)
        VALUES ( ?, ?)
        """,
        (Model, Location),
    )

    conn.commit()
    conn.close()


def insert_ColonoscopySession(DoctorID, PatientID, DeviceID, SessionDateTime):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO ColonoscopySession (DoctorID, PatientID, DeviceID, SessionDateTime)
        VALUES ( ?, ?, ?, ?)
        """,
        (DoctorID, PatientID, DeviceID, SessionDateTime),
    )

    conn.commit()
    conn.close()


def insert_ColonoscopyImage(SessionID, ImagePath):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO ColonoscopyImage ( SessionID, ImagePath)
        VALUES ( ?, ?)
        """,
        (SessionID, ImagePath),
    )

    conn.commit()
    conn.close()


def insert_DetectionModel(ModelName, ModelVersion):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO DetectionModel (ModelName, ModelVersion)
        VALUES (?, ?)
        """,
        (ModelName, ModelVersion),
    )

    conn.commit()
    conn.close()


def insert_DetectedPolyps(ImageID, DetectionModelID, Count):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO DetectedPolyps (ImageID, DetectionModelID, Count)
        VALUES (?, ?, ?)
        """,
        (ImageID, DetectionModelID, Count),
    )

    conn.commit()
    conn.close()


def insert_SegmentationModel(ModelName, ModelVersion):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO SegmentationModel (ModelName, ModelVersion)
        VALUES (?, ?)
        """,
        (ModelName, ModelVersion),
    )

    conn.commit()
    conn.close()


def insert_SegmentationOutput(PolypID, SegmentationModelID, ImagePath):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO SegmentationOutput (PolypID, SegmentationModelID, ImagePath)
        VALUES (?, ?, ?)
        """,
        (PolypID, SegmentationModelID, ImagePath),
    )

    conn.commit()
    conn.close()


def query_EndoscopeDevice(id_num):
    conn = sqlite3.connect("colonoscopy_management.db")
    c = conn.cursor()

    c.execute(
        """
        SELECT * FROM EndoscopeDevice WHERE ID = ?
        """,
        (id_num,),
    )

    result = c.fetchone()
    conn.close()
    return result
