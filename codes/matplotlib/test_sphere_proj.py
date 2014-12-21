# a simple test program to make sure we are plotting data on spheres
# (with the various projections) correctly.


import pylab
from mpl_toolkits.basemap import Basemap
import numpy
import dataRead
import math


# worker function to translate Cartesian data to longitude and
# latitude
def convert_xyz_to_lonlat(x,y,z):

    SMALL = 1.e-100 # prevent divide by zero

    if (x == 0.0):
        x += SMALL

    if (y == 0.0):
        y += SMALL

    if (z == 0.0):
        z += SMALL


    # compute the spherical (polar) coordinates point
    # here theta is the angle from the z-axis (theta = 0 is the north pole)
    R = numpy.sqrt(x**2 + y**2 + z**2)
    rho = numpy.sqrt(x**2 + y**2)

    theta = numpy.arctan2(rho,z)*180.0/math.pi
    phi = numpy.arctan2(y,x)*180.0/math.pi  

    # latitude and longitude -- pretty easy, but latitude is +90 at the
    # north pole, so convert
    lon = phi
    lat = 90.0 - theta

    return (lon,lat)



#-----------------------------------------------------------------------------
# octant data
#-----------------------------------------------------------------------------

# see http://www.scipy.org/Cookbook/Matplotlib/Maps

# here, the lat_0 and lon_0 specify the point directly under
# the viewer (only needed for some projections)

# see http://matplotlib.github.com/basemap/users/mapsetup.html
# for examples of the projections

map = Basemap(projection='ortho', lat_0 = 45, lon_0 = 45,
              resolution = 'l', area_thresh = 1000.)


map.drawmapboundary()

map.drawmeridians(numpy.arange(0, 360, 15), color="0.5", latmax=90)
map.drawparallels(numpy.arange(-90, 90, 15), color="0.5", latmax=90) #, labels=[1,0,0,1])

# draw the boundary of our domain -- we want great circles here
lats = [0,0,90,0]
lons = [0,90,0,0]

n = 1
while (n < len(lats)):
    map.drawgreatcircle(lons[n-1], lats[n-1], lons[n], lats[n], linewidth=2, color="r")
    n += 1



# <<< point on +z >>>
x = 0
y = 0
z = 1

(lon,lat) = convert_xyz_to_lonlat(x,y,z)

xp,yp = map(lon,lat)

s = pylab.text(xp, yp, "+Z", color="b", zorder=10)


# <<< point on +y >>>
x = 0
y = 1
z = 0

(lon,lat) = convert_xyz_to_lonlat(x,y,z)

xp,yp = map(lon,lat)

s = pylab.text(xp, yp, "+Y", color="b", zorder=10)


# <<< point on +x >>>
x = 1
y = 0
z = 0

(lon,lat) = convert_xyz_to_lonlat(x,y,z)

xp,yp = map(lon,lat)

s = pylab.text(xp, yp, "+X", color="b", zorder=10)


f = pylab.gcf()
f.set_size_inches(6.0,8.0)
 

pylab.savefig("test_sphere_proj_octant.png")



#-----------------------------------------------------------------------------
# full sphere data
#-----------------------------------------------------------------------------

pylab.clf()

# see http://www.scipy.org/Cookbook/Matplotlib/Maps

# here, the lat_0 and lon_0 specify the point directly under
# the viewer (only needed for some projections)

# see http://matplotlib.github.com/basemap/users/mapsetup.html
# for examples of the projections

map = Basemap(projection='moll', lon_0 = 0,
              resolution = 'l', area_thresh = 1000.)


map.drawmapboundary()

map.drawmeridians(numpy.arange(0, 360, 15), color="0.5", latmax=90)
map.drawparallels(numpy.arange(-90, 90, 15), color="0.5", latmax=90) #, labels=[1,0,0,1])


# <<< point on +z >>>
x = 0
y = 0
z = 1

(lon,lat) = convert_xyz_to_lonlat(x,y,z)

xp,yp = map(lon,lat)

s = pylab.text(xp, yp, "+Z", color="b", zorder=10)


# <<< point on -z >>>
x = 0
y = 0
z = -1

(lon,lat) = convert_xyz_to_lonlat(x,y,z)

xp,yp = map(lon,lat)

s = pylab.text(xp, yp, "-Z", color="b", zorder=10)


# <<< point on +y >>>
x = 0
y = 1
z = 0

(lon,lat) = convert_xyz_to_lonlat(x,y,z)

xp,yp = map(lon,lat)

s = pylab.text(xp, yp, "+Y", color="b", zorder=10)


# <<< point on -y >>>
x = 0
y = -1
z = 0

(lon,lat) = convert_xyz_to_lonlat(x,y,z)

xp,yp = map(lon,lat)

s = pylab.text(xp, yp, "-Y", color="b", zorder=10)


# <<< point on +x >>>
x = 1
y = 0
z = 0

(lon,lat) = convert_xyz_to_lonlat(x,y,z)

xp,yp = map(lon,lat)

s = pylab.text(xp, yp, "+X", color="b", zorder=10)


# <<< point on -x >>>
x = -1
y = 0
z = 0

(lon,lat) = convert_xyz_to_lonlat(x,y,z)

xp,yp = map(lon,lat)

s = pylab.text(xp, yp, "-X", color="b", zorder=10)


f = pylab.gcf()
f.set_size_inches(6.0,8.0)
 

pylab.savefig("test_sphere_proj_full.png")

