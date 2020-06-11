import tensorflow as tf

# load graph
# modified from: https://stackoverflow.com/questions/45191525/import-a-simple-tensorflow-frozen-model-pb-file-and-make-prediction-in-c

def load_graph(frozen_graph_filename):
    # We load the protobuf file from the disk and parse it to retrieve the 
    # unserialized graph_def
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we can use again a convenient built-in function to import a graph_def into the 
    # current default Graph
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def,
            name=""
        )
    return graph

def pred(pb_file):
    # We use our "load_graph" function
    graph = load_graph(pb_file)

    num_detections = graph.get_tensor_by_name('num_detections:0')
    detection_scores = graph.get_tensor_by_name('detection_scores:0')
    detection_boxes = graph.get_tensor_by_name('detection_boxes:0')
    detection_classes = graph.get_tensor_by_name('detection_classes:0')
    image_tensor = graph.get_tensor_by_name('image_tensor:0')

    sess = tf.Session(graph=graph)
    y = [num_detections,
            detection_scores,
            detection_boxes,
            detection_classes,
        ]

    return sess, y
