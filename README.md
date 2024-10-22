# import_memos_db_from_md
I used OneNote for a long time, but it's hard to use when number of notes getting larger because its bad searching mechanism. Its totally rubbish when searching Chinese terms. I decided to switch to [memos](https://www.usememos.com/) and I had to find a way to migrate all my notes into memos platform. 

## The following is how I use this code

- I installed a OneNote plugin [OneMore](https://onemoreaddin.com/), and export all the notes in markdown format. I placed all notes in one tab in a folder named this tag. 
- stop the memos server and transfer the sqlite db file from server to local. The path of the file might be ~/.memos/memos_prod.db
- modify the DIR_PATH to exact path storing the exported mds then run this script python import_memos_db_from_md.py
- transfer the modified sqlite db file to server and replace the old one.
- start the memos server and start new life with memos.

## something you need to know

I use cloudflare for data storage, it's compatible with memos s3 api and free to use within 10Gb. So change the related settings befor using the script.
change VISIBILITY if you need to use your own settings. Default is PRIVATE except for tag ***collections***.