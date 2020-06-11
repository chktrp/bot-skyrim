import cv2, time, os, random, threading
import numpy as np
from libs.grabscreen import grab_screen
from libs.directkeys import MoveMouse, PressKey, ReleaseKey, W, A, S, D, X, F9
import libs.mytf as tf
import libs.obj_mgr as obj_mgr

# game resolution capture directly from screen
# (xmin, ymin, xmax, ymax)
game_bounding_box = (8, 37, 607, 510)

pb_file = 'models/trained/frozen_inference_graph.pb'
sess, y = tf.pred(pb_file)

wait_for_ready = 5 # seconds before control actually start
max_iter = 500 # number of iteration before terminate itself

action = 0 # current action

target_x = 0 # horizontal distance from the nearest target
target_x_mean = 0 # horizontal distance from all visible enemies
target_bottom = 0.5 # bottom of the nearest target
target_top = 0.5 # top of the nearest target
target_dist = 0  # euclidian distance from the nearest target

iter_ = 0 # current iteration

# only working with foe_id for now
friend_id = 1 # imperial
foe_id = 2 # stormcloak
door_id = 3 # door

look_speed = 40 # pixels to move cursor
min_to_x = 10 # if there's an anemy, move camera for at least at this value
last_attack_ts = 0 # last attack timestamp
min_attack_duration = 0.4 # hold attack key for at least this second
max_attack_duration = 2.5 # release attack key after this 
attack_width = 0.03 # attack if target_x is within this
danger_bottom = 0.7 # backstep if target_bottom is greater than this
chase_bottom = 0.5 # chase if target_bottom is lower than this 
max_target_width = 0.6 # a person shouldn't wider than this

idle_time_max = 20 # while action==0, player will stay if this value>0
idle_time = 0 # if it reaches 0, look around for enemies offscreen
bored_limit = -80 # if idle_time is less than this, reload the save

frame_width = 300
frame_height = 300

winname = 'view'
cv2.namedWindow(winname)        # Create a named window
cv2.moveWindow(winname, game_bounding_box[2],0)  # Move it to (40,30)
cv2.resizeWindow(winname, frame_width, frame_height)
ai_view = []

print('control will start in', wait_for_ready, 'seconds')
print('make sure the game window is active before then')
print('have fun! :D')

def update_nearest():
    global action, last_attack_ts
    global target_x, target_x_mean, target_bottom, target_top, target_dist, iter_
    global y, sess
    global idle_time, idle_time_max, bored_limit
    global ai_view

    while iter_ < max_iter or max_iter < 0 or idle_time > bored_limit:

        screen = grab_screen(region = game_bounding_box)
        screen = screen[:,:,:3]
        cur_frame = cv2.resize(screen,(300, 300))
        inp = cur_frame[:,:,:3]

        input_image = inp.reshape(1, inp.shape[0], inp.shape[1], 3)

        out = sess.run( y, feed_dict={'image_tensor:0': input_image} )

        obj_mgr.localize_detections(out)
        cur_objs = obj_mgr.get_cur_objs()

        # look through all detections
        target_x = 0
        target_x_sum = 0
        target_num = 0
        target_bottom = 0.5
        target_top = 0.5
        target_dist = 0
        
        action = 0

        for obj in cur_objs:
            if (obj['class_id'] == foe_id and
            obj['near'] > target_dist and 
            obj['width'] < max_target_width # it sometimes detects floor as enemy
            ):

                target_x = obj['x_center']-0.5
                target_top = obj['bbox'][0]
                target_bottom = obj['bbox'][2]
                target_dist = obj['near']

                target_x_sum += target_x
                target_num += 1

                x = obj['bbox'][1] * frame_width
                y_ = obj['bbox'][0] * frame_height
                right = obj['bbox'][3] * frame_width
                bottom = obj['bbox'][2] * frame_height

                last_attack_ts = time.time()
                idle_time = idle_time_max
                action = 2
        
        if target_num > 0:
            target_x_mean = target_x_sum/target_num
        else:
            idle_time -= 1

        if action == 2:
            cv2.rectangle(inp, (int(x), int(y_)), (int(right), int(bottom)), (0,0,255), thickness=2)
        
        ai_view = inp

        time.sleep(0.00001)


class myThread (threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)

   def run(self):
       update_nearest()

def main():
    global iter_, last_attack_ts
    global target_dist, target_bottom, target_top, target_x, target_x_mean
    global min_attack_duration, max_attack_duration
    global idle_time, idle_time_max, bored_limit
    global winname, ai_view

    paused = False

    screen = grab_screen(region = game_bounding_box)
    cur_frame = cv2.resize(screen,(300, 300))
    inp = cur_frame[:,:,:3]
    ai_view = inp

    input_image = inp.reshape(1, inp.shape[0], inp.shape[1], 3)
    _ = sess.run( y, feed_dict={'image_tensor:0': input_image} )

    cv2.imshow(winname, ai_view)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        pass

    # count down
    for i in list(range(wait_for_ready))[::-1]:
        print(i + 1)
        time.sleep(1)

    thread1 = myThread()
    thread1.start()

    to_x = 0
    to_y = 0

    while(iter_ < max_iter or max_iter <= 0 or idle_time > bored_limit):
        if not paused:
            log_str = ''

            ts = time.time()

            if action == 0:
                # stop
                if idle_time > 0:
                    # hold
                    to_x = 0
                elif idle_time > bored_limit:
                    # where are they?
                    log_str += '? (' + str(abs(idle_time)) + '/' + str(abs(bored_limit)) + ') '
                    if target_x_mean > 0:
                        to_x = look_speed*0.5
                    else:
                        to_x = -look_speed*0.5

                else:
                    # idle for too long, reload the save
                    PressKey(F9)
                    time.sleep(0.1)
                    ReleaseKey(F9)
                    idle_time = idle_time_max*2

                to_y = 0

                ReleaseKey(A)
                ReleaseKey(W)
                ReleaseKey(D)
                ReleaseKey(S)

                if ts - last_attack_ts > min_attack_duration:
                    ReleaseKey(X)

            elif action == 2:
                # side step
                if target_x_mean < 0:
                    to_x = look_speed*target_x - min_to_x

                    ReleaseKey(A)
                    PressKey(D)
                
                elif target_x_mean > 0:
                    to_x = look_speed*target_x + min_to_x

                    ReleaseKey(D)
                    PressKey(A)
                else:
                    to_x = 0
                    to_y = 0
                
                # move the camera down a bit for better view
                if target_top > 0.2 and target_bottom > 0.9:
                    # look down
                    to_y = 1
                elif target_top < 0.1 and target_bottom < 0.8:
                    # look up
                    to_y = -1
                else:
                    to_y = 0
                
                if target_bottom > danger_bottom:
                    # backstep
                    log_str += 'back '
                    PressKey(S)
                elif target_bottom > 0 and target_bottom < chase_bottom:
                    # chase
                    log_str += 'forward '
                    PressKey(W)


                if ts - last_attack_ts > max_attack_duration:
                    ReleaseKey(X)

                if abs(target_x) < attack_width:
                    # attack
                    log_str += 'attack '
                    PressKey(X)
            
            MoveMouse(int(to_x), dest_y=int(to_y))

            iter_ += 1
            print('step', iter_, '/'+str(max_iter), '  ', log_str)

            cv2.imshow(winname, ai_view)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.0001)

    # release everything
    ReleaseKey(A)
    ReleaseKey(W)
    ReleaseKey(D)
    ReleaseKey(S)
    ReleaseKey(X)
        
    cv2.destroyAllWindows()
            
if __name__ == "__main__":
    main()