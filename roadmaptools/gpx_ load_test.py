
import roadmaptools.inout

from roadmaptools.printer import print_info
from roadmaptools.init import config

print_info("Loading start")
#oadmaptools.inout.load_gpx("/home/fido/AIC data/Shared/EXPERIMENTAL/traces/traces-raw.gpx")
roadmaptools.inout.load_gpx('/home/olga/Documents/GPX/test1.gpx')
print_info("Loading end")