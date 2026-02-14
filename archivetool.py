from pathlib import Path
from datetime import datetime
import db, hashlib, argparse, logging, os, zipfile
#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s %(message)s')

"""
SQLite needs:
Files scanned
Hashes of files to ensure data validity
Last backup date
Initialized/Creation date
Files in Archive database
"""
def main():
    archivetoolcommands = argparse.ArgumentParser(
        prog="archive-tool.py",
        description="Ryan Ruddock's first run at making an archiving tool with an SQLite database and CLI arguments")

    commands = archivetoolcommands.add_subparsers(required=True)

    initcmd=commands.add_parser("init")
    initcmd.set_defaults(func=init)

    scancmd=commands.add_parser("scan")
    scancmd.set_defaults(func=scan)
    scancmd.add_argument("filepath")
    scancmd.add_argument("--mode", choices=["hash","mtime"],
         default="hash")
    # scancmd.add_argument("--mtime, -mt, " \
    #     "action='store_true'")

    archivecmd=commands.add_parser("archive")
    archivecmd.set_defaults(func=archive)
    archivecmd.add_argument("archive_filename")
    

    statuscmd=commands.add_parser("status")
    statuscmd.set_defaults(func=status)

    args=archivetoolcommands.parse_args()
    args.func(args)

def init(args):
    print("[INIT] Beginning database initilization")
    connect_db=None
    try:
        connect_db=db.connect_to_db(db.db)
        print("[INIT] Connection to database established")
        if connect_db:
                db.create_database_table(connect_db)
                print("[INIT] Database ready")
    finally:
        if connect_db:
            connect_db.close()
            print("[INIT] Disconnected from Database.")
    


def scan(args):
    path=Path(args.filepath)
    mode=args.mode
    logging.info(f"[SCAN] {mode}")
    connect_db=None
    print(f"[SCAN] Beginning scan of provided directory: {os.path.abspath(path)}")
    db_entry(connect_db,path,mode)


#If a file was archived, it should be marked as ineligible when scanned again (unless changed, obviously).
def db_entry(connect_db,path,mode):
    try:
        connect_db=db.connect_to_db(db.db)
        print("[SCAN] Connection to database established\n")
        if connect_db:
                pathlistwalk=[]
                pathlistdb=db.pull_paths_from_db(connect_db)
                if path.exists():
                    try:
                        for cwd, folders, files in path.walk():
                            try:
                                for file in files:
                                    filepath=Path(cwd/file)
                                    absolutepath=(os.path.abspath(filepath))
                                    pathlistwalk.append(absolutepath)
                                    stats=filepath.stat()
                                    mtime=stats.st_mtime
                                    size=stats.st_size
                                    humantime=datetime.fromtimestamp(stats.st_mtime)
                                    hashobject= hashlib.md5()
                                    with open(absolutepath, "rb") as fileopen:
                                        for chunk in iter(lambda:fileopen.read(8192), b""):
                                            hashobject.update(chunk)
                                    hashid=hashobject.hexdigest()
                                    print(f"[SCAN] Info for: {absolutepath}\n[SIZE]: {size} BYTES\n[MTIME] {mtime}\n[READABLE TIME] {humantime}\n[HASH] {hashid}")
                                    db.insert_file_metadata(connect_db, hashid, absolutepath, size, mtime, mode)
                            except PermissionError:
                                print(f"[SCAN] [ERROR] Error, insufficient permissions to read {cwd}")
                        if pathlistdb != []:
                            absolutepath=os.path.abspath(path)
                            pathlistpostcheck=[]
                            for entries in pathlistdb:
                                if absolutepath in entries:
                                    pathlistpostcheck.append(entries)
                            logging.info(f"[ENTRIES IN DB MATCHING SCAN PATH]: {pathlistpostcheck}")
                            for entries in pathlistpostcheck:
                                if entries not in pathlistwalk:
                                    print(f"[SCAN] [CAUTION] {entries} is in database but doesn't exist in path!")
                                    db.store_failure("File no longer exists at path",connect_db,entries)
                        print("[SCAN] Scan complete. Disconnecting from Database...")
                    except PermissionError:
                        print(f"[SCAN] [ERROR] Error, insufficient permissions to read {path}")
                elif not path.exists():
                    print("[SCAN] [ERROR] Path does not exist.")
    finally:
        if connect_db:
            connect_db.close()
            print("[SCAN] Disconnected from Database.")
    

def status(args):
    connect_db=db.connect_to_db(db.db)
    db.gather_status_statistics(connect_db)

def archive(args):
    archivename=args.archive_filename
    archivepath=f"{Path.cwd()/archivename}"
    print(f"[ARCHIVE] Using {archivepath} as path for provided archive input")
    logging.info(f"{archivepath} Archive file destination")
    connect_db=db.connect_to_db(db.db)
    archivefilelist=db.pull_eligible_filepaths(connect_db)
    if archivefilelist==[]:
        print("[ARCHIVE] No files eligible to be archived. Disconnecting Database...")
        connect_db.close()
        print("[ARCHIVE] Disconnected from database")
        return
    print("[ARCHIVE] List of files to be archived:")
    for filestobearchived in archivefilelist:
        print(f"[ARCHIVE] {filestobearchived}")
    logging.info(f"{archivefilelist} literal list of files to be archived")
    archivefile=zipfile.ZipFile(archivepath, "w")
    successfully_archived=archive_file_list(archivefilelist,archivefile,connect_db)
    print("[ARCHIVED] Files successfully archived:")
    for filesarchived in successfully_archived:
        print(f"[ARCHIVED] {filesarchived}")
    db.mark_entries_as_archived(connect_db, successfully_archived)
    connect_db.close()
    print("[ARCHIVE] Archiving complete. Disconnecting from Database...\n[ARCHIVE] Disconnected from database")

    
    
def archive_file_list(archivefilelist,archivefile,dbconnection):
    successfully_archived=[]
    for file in archivefilelist:
        try:
            archivefile.write(file, compress_type=zipfile.ZIP_DEFLATED)
            successfully_archived.append(file)
        except Exception as error:
            logging.debug(error)
            error=str(error)
            db.store_failure(error,dbconnection,file)
    archivefile.close()
    logging.info(f"List of successfully archived files: {successfully_archived}")
    return successfully_archived
    

if __name__ == "__main__":
    main()

