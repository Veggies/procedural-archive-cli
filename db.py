import sqlite3, logging
from pathlib import Path
db=Path.cwd()/"archive-tool.sqlite3"
#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s %(message)s')

def connect_to_db(db):
    try:
        database=sqlite3.connect(db)
        return database
    #print("Connected to db")
    except sqlite3.OperationalError:
                raise Exception("Error, insufficient permissions to write to Database.")
    






def create_database_table(db): 
    try:
        cursor=db.cursor()   
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY NOT NULL,
            hash TEXT,
            size INTEGER NOT NULL,
            modified FLOAT NOT NULL,
            eligibility BOOL NOT NULL CHECK (eligibility IN (0, 1)),
            eligibilitynote TEXT NOT NULL,
            errornote TEXT,        
            archived BOOL,
            state TEXT
        );
    """)
        db.commit()
    except sqlite3.OperationalError:
        raise Exception("Error, insufficient permissions to write to Database.")






def insert_file_metadata(db,hash,path,size,modified,mode):
    update,eligibility,eligibilitynote=check_metadata_status(db,hash,path,modified,mode,size)
    check_metadata_validity(hash,path,size,modified,eligibility,eligibilitynote,update)
    if update:
        update_existing_metadata(db,hash,path,size,modified,eligibility,eligibilitynote)
    elif update==None:
        create_new_metadata(db,hash,path,size,modified,eligibility,eligibilitynote)
    elif update==False:
        print(f"[SCAN] No changes were detected for {path}\n")
        return




def check_metadata_status(db,hash,path,modified,mode,size):
    logging.info(f"[CHECK METADATA STATUS] Check path: {path}")
    update=None
    if mode=="hash":
        cursor=db.cursor()
        entries=cursor.execute(
        """
        SELECT hash, path, eligibility, eligibilitynote, archived
        FROM files
        WHERE path = ?
        """,
        (path,)
    )
        row=entries.fetchone()
        update,eligibility,eligibilitynote=check_metadata_helper(row,hash,"Hash",path,size)
        if eligibility==True:
            eligibility=1
        elif eligibility==False:
            eligibility=0
        return update,eligibility,eligibilitynote

    elif mode=="mtime":
        cursor=db.cursor()
        entries=cursor.execute(
        """
        SELECT modified, path, eligibility, eligibilitynote, archived
        FROM files
        WHERE path = ?
        """,
        (path,)
    )
        row=entries.fetchone()
        update,eligibility,eligibilitynote=check_metadata_helper(row,modified,"Modified Time",path,size)
        if eligibility==True:
            eligibility=1
        elif eligibility==False:
            eligibility=0
        return update,eligibility,eligibilitynote
    
        

def check_metadata_helper(row,checkvalue,checktype,path,size):
    logging.info(f"[CHECK HELPER] {path} INFO: {row}")
    if row != None:
        logging.info(f"[ROW INFO]{row}")
        logging.info(f"[CHECK VALUE]{row[0]} {checkvalue}")
        if checkvalue == row[0]:
            logging.info(f"[LOG.INFO] {checktype} for {path} has not changed. No update required.")
            update=False
            eligibility=row[2]
            eligibilitynote=row[3]
            if row[4]==1 and row[2]==0:
                eligibility=row[2]
                eligibilitynote=row[3]
                update=False
                return update,eligibility,eligibilitynote
            elif row[4]==1:
                logging.info("[ARCHIVED STATUS] archived")
                eligibility=0
                eligibilitynote="filearchived"
                update=True
                return update, eligibility,eligibilitynote
            return update,eligibility,eligibilitynote
        elif checkvalue != row[0]:
            logging.info("[LOG.INFO] File metadata needs to be updated.")
            eligibility,eligibilitynote=eligiblity_check(path,size)
            update=True
            return update, eligibility,eligibilitynote
    elif row==None:
        update=None
        eligibility,eligibilitynote=eligiblity_check(path,size)
        return update,eligibility,eligibilitynote
    


def check_metadata_validity(hash,path,size,modified,eligibility,eligibilitynote,update):
    if not isinstance(hash, str):
        raise Exception("hash must be string")

    if not isinstance(path, str):
        raise Exception("path must be string")

    if not isinstance(size, int):
        raise Exception("size must be int")

    if not isinstance(modified, (int, float)):
        raise Exception("modified must be numeric")

    if eligibility not in (0,1):
        raise Exception(f"{eligibility} eligibility must be 0 or 1")

    if not isinstance(eligibilitynote, (str)):
        raise Exception(f"{eligibilitynote} eligibilitynote must be string")

    if update not in (True, False, None):
        raise Exception("update must be True/False/None")
    return
    



def eligiblity_check(path,size):
    eligiblity=True
    eligiblitynote=""
    if size > 10737418240:
        eligiblity=False
        eligiblitynote+=f"[SIZE] File is too large ({size} bytes)"
    pathbyte=len(path.encode('utf-8'))
    if pathbyte > 4096:
        eligiblity=False
        eligiblitynote+=f"[PATH] File path is too long ({pathbyte} bytes)"
    logging.info(f"[ELIGIBILITY] {eligiblity}")
    logging.info(f"[ELIGIBILITY NOTES] {eligiblitynote}")
    return eligiblity, eligiblitynote



def update_existing_metadata(db,hash,path,size,modified,eligibility,eligibilitynote):
    if eligibilitynote=="filearchived":
        logging.info(f"[ARCHIVED FILE] Updating eligibility to NO for {path}")
        cursor=db.cursor()
        entries=cursor.execute(
        """
        UPDATE files
        SET hash=?, size=?, modified=?, eligibility=?, eligibilitynote=?
        WHERE path = ?
        """,
        (hash, size, modified, eligibility, eligibilitynote, path)
    )
        db.commit()
        print(f"[SCAN] {path} was archived, changing eligibility to No and eligibility note to archived\n")
        return
    

    cursor=db.cursor()
    entries=cursor.execute(
    """
    UPDATE files
    SET hash=?, size=?, modified=?, eligibility=?, eligibilitynote=?, errornote=NULL, archived=0, state='updated-scanned'
    WHERE path = ?
    """,
    (hash, size, modified, eligibility, eligibilitynote, path)
)
    db.commit()
    print(f"[SCAN] Updating entry for {path}\n[SCAN] Setting state as updated-scanned\n")





def create_new_metadata(db,hash,path,size,modified,eligibility,eligibilitynote):
    logging.info(f"[SCAN] Creating entry for {path}\n[SCAN] Setting state as new-scanned")
    cursor=db.cursor()
    cursor.execute(
    """
    INSERT OR IGNORE INTO files (hash, path, size, modified, eligibility, eligibilitynote, state)
    VALUES (?, ?, ?, ?, ?, ?, "new-scanned")
    """,
    (hash, path, size, modified, eligibility, eligibilitynote)
)
    db.commit()
    print(f"[SCAN] Creating entry for {path}")
    print(f"[SCAN] Setting state as new-scanned\n")



    


def pull_eligible_filepaths(db):
    cursor=db.cursor()
    pullpaths=cursor.execute(
    """
    SELECT path
    FROM files
    WHERE eligibility = 1 
        AND (archived = 0 OR archived IS NULL)
    """
    )
    rows=pullpaths.fetchall()
    logging.debug(f"{rows} tuples fetched from database")
    archivefilelist=[]
    for filepaths in rows:
        for paths in filepaths:
            logging.info(f"{paths} added to list of files to archive")
            archivefilelist.append(paths)
    return archivefilelist

def mark_entries_as_archived(db,archivefilelist):
    cursor=db.cursor()
    for file in archivefilelist:
        cursor.execute(
        """
        UPDATE files
        SET archived=1, state='archived'
        where path = ?
        """,
        (file,)
        )
    db.commit()

def store_failure(errorlog,dbconnection,filepath):
        cursor=dbconnection.cursor()
        cursor.execute(
        """
        UPDATE files
        SET eligibility=0, errornote=?, state='error'
        where path = ?
        """,
        (errorlog,filepath,)
        )
        dbconnection.commit()
        logging.info(f"{filepath} encountered {errorlog}, stored in Database")


#files archived, files with errors, ineligibile files, total files
def gather_status_statistics(dbconnection):
    cursor=dbconnection.cursor()
    status=cursor.execute(
    """
    SELECT state, COUNT(*)
    from files
    GROUP BY state;
    """
    )
    status=status.fetchall()
    if status==[]:
        print("DATABASE EMPTY")
        return
    print("===============\nSTATUS OF FILES\n===============")
    for state, count in status:
        print(f"{state.capitalize()}: {count}")


def pull_paths_from_db(dbconnection):
    cursor=dbconnection.cursor()
    paths=cursor.execute(
    """
    SELECT path
    from files
    GROUP BY path;
    """
    )
    paths=paths.fetchall()
    pathlistdb=[]
    for path in paths:
        pathlistdb.append(path[0])
    return pathlistdb