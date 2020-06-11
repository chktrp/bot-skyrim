import math

min_detection_score = 0.65 # valid detections should have score more than this

cur_objs = []
cur_bbs = []

def localize_detections(detections, reset_cur_objs = True, score_threshold = min_detection_score):
    global cur_objs, cur_bbs

    num_detections = int(detections[0][0])

    if reset_cur_objs:
        cur_objs = []
        cur_bbs = []
    
    for i in range(num_detections):
        classId = int(detections[3][0][i])
        score = float(detections[1][0][i])
        bbox = [float(v) for v in detections[2][0][i]]
        if score > score_threshold:
            class_id = classId
            obj_center = ((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2)
            obj_height = (bbox[2]-bbox[0])
            obj_width = (bbox[3]-bbox[1])

            obj = {'class_id': class_id,
                    'x_center': obj_center[1],
                    'y_center': obj_center[0],
                    'width': obj_width,
                    'height': obj_height,
                    'bbox': bbox,
                    'near':bbox[0]+obj_height,
                    'score': score
                    }

            cur_objs.append(obj)
            cur_bbs.append(bbox)

def get_cur_bbs():
    global cur_bbs
    return cur_bbs

def get_cur_objs():
    global cur_objs
    return cur_objs
