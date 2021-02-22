# bwsfv

An application to verify file consistency with .sfv files.


## Preamble

I have created several PyQt applications in the past. I tried PyGTK+ a long
time ago, but didn't really care for it then. I wanted to give PyGObject a shot
since I noticed it was fairly simple looking code nowadays. To my amazement,
PyGObject is very easy to develop with.

I started this application just to see how fast and easily I could do a simple
desktop application. This is nowhere near complete, but we'll see how it goes
in the future!


## Running on Linux

### Installing dependencies (Debian-based systems)
Open your terminal application and type:
`sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0`

Hit enter. Enter your password when prompted. Answer yes to the question about
using additional disk space.

### Downloading the source
git clone https://github.com/bulkware/bwsfv.git

### Running the application
Enter the application directory using this command:
`cd bwsfv`

You can run the application from the source code using this command:
`python3 src/bwsfv.py`
