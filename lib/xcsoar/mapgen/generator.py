import os.path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
import time
from xcsoar.mapgen.terrain import srtm
from xcsoar.mapgen.topology import shapefiles
from xcsoar.mapgen.georect import GeoRect
from xcsoar.mapgen.filelist import FileList
from xcsoar.mapgen.downloader import Downloader

class Generator:
    def __init__(self, dir_data, dir_temp):
        '''
        Constructor of the MapGenerator class
        @param dir_data: Path of the data folder
        @param dir_temp: Path of the temporary folder
        '''
        self.__downloader = Downloader(dir_data)

        self.__dir_temp = os.path.abspath(dir_temp)
        if not os.path.exists(self.__dir_temp):
            os.mkdir(self.__dir_temp)

        self.__bounds = None
        self.__files = FileList()

    def add_information_file(self, name, author = 'unknown'):
        '''
        Adds an information file to the map
        '''
        if self.__bounds == None:
            raise RuntimeError("Please set bounds before calling add_information_file() !")

        dst = os.path.join(self.__dir_temp, "info.txt")
        f = open(dst, 'w')
        try:
            f.write("map name: " + name +\
                        "\ngenerator: XCSoar Map Generator" +\
                        "\ncreation time: " + time.strftime("%d.%m.%Y %H:%M:%S") + " (" + str(time.time()) +\
                        ")\nlatitude range: " + str(self.__bounds.bottom) + " to " + str(self.__bounds.top) +\
                        "\nlongitude range: " + str(self.__bounds.left)   + " to " + str(self.__bounds.right) + "\n")
            if author != None and author != '':
                f.write('author: ' + author + "\n")
        finally:
            f.close()

        self.__files.add(dst, True)

    def add_waypoint_file(self, filename):
        '''
        Adds a waypoint file to the map
        @param filename: The file that should be added
        '''
        print("Adding waypoint file...")
        if not os.path.exists(filename):
            raise RuntimeError("Waypoint file " + filename + " not found!")

        dst = os.path.join(self.__dir_temp, "waypoints.xcw")
        shutil.copy(filename, dst)
        if not os.path.exists(dst):
            raise RuntimeError("Copying " + os.path.basename(filename) + " to " + dst + " failed!")

        self.__files.add(dst, True)

    def add_waypoint_details_file(self, filename):
        '''
        Adds a waypoint details file to the map
        @param filename: The file that should be added
        '''
        print("Adding waypoint details file...")
        if not os.path.exists(filename):
            raise RuntimeError("Waypoint details file " + filename + " not found!")

        dst = os.path.join(self.__dir_temp, "airfields.txt")
        shutil.copy(filename, dst)
        if not os.path.exists(dst):
            raise RuntimeError("Copying " + os.path.basename(filename) + " to " + dst + " failed!")

        self.__files.add(dst, True)

    def add_airspace_file(self, filename):
        '''
        Adds a airspace file to the map
        @param filename: The file that should be added
        '''
        print("Adding airspace file...")
        if not os.path.exists(filename):
            raise RuntimeError("Airspace file " + filename + " not found!")

        dst = os.path.join(self.__dir_temp, "airspace.txt")
        shutil.copy(filename, dst)
        if not os.path.exists(dst):
            raise RuntimeError("Copying " + os.path.basename(filename) + " to " + dst + " failed!")

        self.__files.add(dst, True)

    def add_topology(self, bounds = None):
        print("Adding topology...")

        if bounds == None:
            if self.__bounds == None:
                raise RuntimeError("Boundaries undefined!")
            bounds = self.__bounds

        self.__files.extend(shapefiles.create(bounds, self.__downloader, self.__dir_temp))

    def add_terrain(self, arcseconds_per_pixel = 9.0, bounds = None):
        print("Adding terrain...")

        if bounds == None:
            if self.__bounds == None:
                raise RuntimeError("Boundaries undefined!")
            bounds = self.__bounds

        self.__files.extend(srtm.create(bounds, arcseconds_per_pixel,
                                        self.__downloader, self.__dir_temp))

    def set_bounds(self, bounds):
        if not isinstance(bounds, GeoRect):
            raise RuntimeError("GeoRect expected!")

        print("Setting map boundaries: " + str(bounds))
        self.__bounds = bounds

    def create(self, filename, attach = False):
        '''
        Creates the map at the given location
        @param filename: Location of the map file that should be created
        '''

        # Open the zip file
        if attach:
            print("Adding MapGenerator data to map file...")
            attach = "a"
        else:
            print("Creating map file...")
            attach = "w"

        z = ZipFile(filename, attach, ZIP_DEFLATED)
        for file in self.__files:
            if os.path.isfile(file[0]):
                # file[1] is the flag if we should compress the file
                z.write(file[0], os.path.basename(file[0]), ZIP_DEFLATED if file[1] else ZIP_STORED)
        z.close()

    def cleanup(self):
        for file in self.__files:
            os.unlink(file[0])
        self.__files.clear()