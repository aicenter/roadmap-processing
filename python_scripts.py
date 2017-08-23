from __future__ import print_function
import time
import subprocess
import codecs


def execute_all_bash():
    exit_code = subprocess.call("cat data/output.geojson | python prune_geojson_file.py | python simplify_graph.py | python speed_from_osm.py | python curvature.py | python postprocess_geojson.py > data/result.geojson", shell=True)
    return exit_code


def clean_geojson():
    from prune_geojson_file import execute
    print("prune_geojson_file.py is running...")
    start_time = time.time()

    input_stream = codecs.open("data/output.geojson", encoding='utf8')
    output_stream = codecs.open("data/output-cleaned.geojson", 'w')

    execute(input_stream, output_stream)
    input_stream.close()
    output_stream.close()

    print("time: %s secs\n" % (time.time() - start_time))


def simplify_geojson():
    from simplify_graph import execute
    print("simplify_graph.py is running...")
    start_time = time.time()

    input_stream = codecs.open("data/output-cleaned.geojson", encoding='utf8')
    output_stream = codecs.open("data/output-simplified.geojson", 'w')

    # l_check set True whether you don't want to simplify edges with different number of lanes
    # c_check set True whether you don't want to simplify edges with different curvature
    execute(input_stream, output_stream, l_check=False, c_check=False)
    input_stream.close()
    output_stream.close()

    print("time: %s secs\n" % (time.time() - start_time))


def get_speed_from_osm():
    from speed_from_osm import execute
    print("speed_from_osm.py is running...")
    start_time = time.time()

    input_stream = codecs.open("data/output-simplified.geojson", encoding='utf8')
    output_stream = codecs.open("data/output-speeds.geojson", 'w')

    execute(input_stream, output_stream)
    input_stream.close()
    output_stream.close()

    print("time: %s secs\n" % (time.time() - start_time))


def get_curvature_of_edges():
    from curvature import execute
    print("curvature.py is running...")
    start_time = time.time()

    input_stream = codecs.open("data/output-speeds.geojson", encoding='utf8')
    output_stream = codecs.open("data/output-curvatures.geojson", 'w')

    execute(input_stream, output_stream)
    input_stream.close()
    output_stream.close()

    print("time: %s secs\n" % (time.time() - start_time))


def postprocessing_geojson():
    from postprocess_geojson import execute
    print("postprocess_geojson.py is running...")
    start_time = time.time()

    input_stream = codecs.open("data/output-curvatures.geojson", encoding='utf8')
    output_stream = codecs.open("data/output-result.geojson", 'w')

    execute(input_stream, output_stream, formated=False)
    input_stream.close()
    output_stream.close()

    print("time: %s secs" % (time.time() - start_time))
