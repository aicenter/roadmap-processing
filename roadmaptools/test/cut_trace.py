import roadmaptools.inout
import roadmaptools.gpx

trace_file = r"C:\AIC data\Shared\Map Matching Benchmark\2015 100 tracks dataset\00000000/trace-period-24.gpx"

gpx_content = roadmaptools.inout.load_gpx(trace_file)

roadmaptools.gpx.cut_trace(gpx_content.tracks[0], 10)

roadmaptools.inout.save_gpx(gpx_content, r"C:\AIC data\Shared\Map Matching Benchmark\test traces/trace_0-period_24-first_10_points.gpx")