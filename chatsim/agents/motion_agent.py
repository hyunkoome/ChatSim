import openai 
import numpy as np
from termcolor import colored
import traceback
import openai
import random
from chatsim.foreground.motion_tools.placement_and_motion import vehicle_motion
from chatsim.foreground.motion_tools.placement_iterative import vehicle_placement, vehicle_placement_specific
from chatsim.foreground.motion_tools.tools import transform_node_to_lane

class MotionAgent:
    def __init__(self, config):
        self.config = config

    def llm_reasoning_dependency(self, scene, message):
        """ LLM reasoning of Motion Agent, determine if the vehicle placement is depend on scene elements.
        Input:
            scene : Scene
                scene object.
            message : str
                language prompt to ChatSim.
        """
        try: 
            q0 = "I will provide an operation statement to add a vehicle, and you need to determine whether the position of the added car has any spatial dependency with other cars in my statement"

            q1 = "Only return a JSON format dictionary as your response, which contains a key 'dependency'. If the added car's position depends on other objects, set it to 1; otherwise, set it to 0."

            q2 = "An Example: Given statement 'add an Audi in the back which drives ahead', you should return {'dependency': 0}. This is because I only mention the added Audi."

            q3 = "An Example: Given statement 'add a Porsche at 2m to the right of the red Audi.', you should return {'dependency': 1}. This is because Porsche's position depends on Audi."

            q4 = "An Example: Given statement 'add a car in front of me.', you should return {'dependency': 0}. This is because 'me' is not other car in the scene."

            q5 = "The statement is:" + message
            
            prompt_list = [q0,q1,q2,q3,q4,q5]

            result = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an assistant helping me to extract information from the operations."}] + \
                     [{"role": "user", "content": q} for q in prompt_list]
            )
            answer = result['choices'][0]['message']['content']

            print(f"{colored('[Motion Agent LLM] analyzing insertion scene dependency ', color='magenta', attrs=['bold'])} \
                    \n{colored('[Raw Response>>>]', attrs=['bold'])} {answer}")

            start = answer.index("{")
            answer = answer[start:]
            end = answer.rfind("}")
            answer = answer[:end+1]
            placement_mode = eval(answer)
            print(f"{colored('[Extracted Response>>>]', attrs=['bold'])} {placement_mode} \n")

        except Exception as e:
            print(e)
            traceback.print_exc()
            return "[Motion Agent LLM] reasoning object dependency fails."

        return placement_mode

    def llm_placement_wo_dependency(self, scene, message):
        try:
            q0 = "I will provide you with an operation statement to add and place a vehicle, and I need you to extract 3 specific placement information from the statement, including: "

            q1 = " (1) 'mode', one of ['front', 'left front', 'left', 'right front', 'right', 'random'], representing approximate initial positions of the vehicle. If not specified, it defaults to 'random'."

            q2 = " (2) 'distance_constraint' indicates whether there's a constraint on the distance of the added vehicle. 0 means no constraint, 1 means there is a constraint." + \
                    " If there's no relevant information mentioned, it defaults to 0."

            q3 = " (3) 'distance_min_max' represents the range of constraints when 'distance_constraint' applicable. It should be a tuple in the format (min, max), for example, (9, 11) means the minimum distance is 9, and the maximum is 11." + \
                    " When there's 'distance_constraint' is 0, the default value is (0, 50). If distance is specified as a specific value 'x', 'distance_min_max' is (x, x+5)"

            q4 = "Just return the json dict with keys:'mode', 'distance_constraint', 'distance_min_max'. Do not return any code or discription."

            q5 = "An Example: Given operation statement: 'Add an Audi 7-10 meters ahead', you should return " + \
                    "{'mode':'front', 'distance_constraint': 1, 'distance_min_max':(7,10)}"

            q6 = "An Example: Given operation statement: 'Add an Porsche in the right front.', you should return " + \
                    "{'mode':'right front', 'distance_constraint': 0, 'distance_min_max':(0,50)}"

            q7 = "Note that you should not return any code or explanations, only provide a JSON dictionary."

            q8 = "The operation statement:" + message

            prompt_list = [q0,q1,q2,q3,q4,q5,q6,q7,q8]

            result = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an assistant helping me to determine how to place a car."}] + \
                        [{"role": "user", "content": q} for q in prompt_list]
            )
            answer = result['choices'][0]['message']['content']

            print(f"{colored('[Motion Agent LLM] deciding scene-independent object placement', color='magenta', attrs=['bold'])} \
                    \n{colored('[Raw Response>>>]', attrs=['bold'])} {answer}")

            start = answer.index("{")
            answer = answer[start:]
            end = answer.rfind("}")
            answer = answer[:end+1]
            placement_prior = eval(answer)
            print(f"{colored('[Extracted Response>>>]', attrs=['bold'])} {placement_prior} \n")

        except Exception as e:
            print(e)
            traceback.print_exc()
            return "[Motion Agent LLM] deciding placement fails."

        return placement_prior

    def llm_placement_w_dependency(self, scene, message, scene_object_description):
        try:
            q0 = "I will provide you with an operation statement to add and place a vehicle, as well as information of other cars in the scene."
            
            q1 = "I need you to determine a specific position (x, y) for placement of the added car in my statement. "

            q2 = "Information of other cars in the scene is a two-level dictionary, with the first level representing the different car id in the scene, " + \
                    "and the second level containing various information about that car, including the (x, y) of its world 3D coordinate, " + \
                    "its image coordinate (u, v) in an image frame, depth, and rgb color representation."

            q3 = "The dictionary is" + str(scene_object_description)

            q4 = "I will also further inform you about the operations that have been previously performed on this scene. " + \
                    "You can use these past operations, along with the dictionary I provide, to generate the final position."

            q5 = "The previously performed operation is : " + str(scene.past_operations)

            q6 = "You should return a placemenet positon in JSON dictionary with 2 keys: 'x', 'y'. Do not provide any code or explanations, only return the final JSON dictionary."

            q7 = "The requirement is:" + message

            prompt_list = [q0,q1,q2,q3,q4,q5,q6,q7]

            result = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an assistant helping me to determine how to place a car."}] + \
                        [{"role": "user", "content": q} for q in prompt_list]
            )
            answer = result['choices'][0]['message']['content']
            print(f"{colored('[Motion Agent LLM] deciding scene-dependent object placement', color='magenta', attrs=['bold'])} \
                    \n{colored('[Raw Response>>>]', attrs=['bold'])} {answer}")

            start = answer.index("{")
            answer = answer[start:]
            end = answer.rfind("}")
            answer = answer[:end+1]
            placement_prior = eval(answer)
            print(f"{colored('[Extracted Response>>>]', attrs=['bold'])} {placement_prior} \n")

        except Exception as e:
            print(e)
            traceback.print_exc()
            return "[Motion Agent LLM] deciding placement fails."

        return placement_prior

    def llm_motion_planning(self, scene, message):
        # motion GPT -> action, speed and direction
        try:
            q0 = "I will provide you with an operation statement to add and place a vehicle, and I need you to determine the its motion situation from my statement, including: "

            q1 = "(1) 'action', one of ['static', 'random', 'straight', 'turn left', 'turn right', 'change lane left', 'change lane right', 'back']. If action not mentioned in the statement, it defaults to 'straight'." + \
                "For example, the statement is 'add a black car in front of me', then the action is 'straight'." 

            q2 = "(2) 'speed', the approximate speed of the vehicle, one of ['random', 'fast', 'slow']. If speed is not mentioned in the statement, it defaults to 'slow'."

            q3 = "(3) 'direction', one of ['away', 'close', 'random']. 'away' represents the direction away from oneself, and 'close' represents the direction toward oneself." + \
                "For example, moving forward is 'away' from oneself, while moving towards oneself is 'close'. If direction is not mentioned in the statement, just return 'random'."
            
            q4 = "(4) 'wrong_way', if the vehicle drives in the wrong way, one of ['true'. 'false']. If the information is not mentioned in the statement, it defaults to 'false'."

            q4 = "An Example: Given the statement 'add a Tesla that is racing straight ahead in the right front of the scene', you should return {'action': 'straight', 'speed': 'acceleration', 'direction': 'away', 'wrong_way': 'false'}"

            q5 = "An Example: Given the statement 'add a yellow Audi in front of the scene', you should return {'action': 'static', 'speed': 'random', 'direction': 'away', 'wrong_way': 'false'}"

            q6 = "An Example: Given the statement 'add a Tesla coming from the front and driving in the wrong way', you should return {'action': 'straight', 'speed': 'random', 'direction': 'close', 'wrong_way': 'true'}"

            q7 = "Note that there is no need to return any code or explanations; only provide a JSON dictionary. Do not include any additional statements."
            
            q8 = "The operation statement is:" + message

            prompt_list = [q0,q1,q2,q3,q4,q5,q6,q7,q8]

            result = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are an assistant helping me to assess the motion situation for adding vehicles."}] + \
                        [{"role": "user", "content": q} for q in prompt_list]
            )
            answer = result['choices'][0]['message']['content']

            print(f"{colored('[Motion Agent LLM] finding motion prior', color='magenta', attrs=['bold'])} \
                    \n{colored('[Raw Response>>>]', attrs=['bold'])} {answer}")

            start = answer.index("{")
            answer = answer[start:]
            end = answer.rfind("}")
            answer = answer[:end+1]
            motion_prior = eval(answer)
            print(f"{colored('[Extracted Response>>>]', attrs=['bold'])} {motion_prior} \n")

        except Exception as e:
            print(e)
            traceback.print_exc()
            return "[Motion Agent LLM] finding motion prior fails."

        return motion_prior


    def func_placement_and_motion_single_vehicle(self, scene, added_car_name):
        added_car_id = added_car_name.lstrip("added_car_")
        transformed_map_data = transform_node_to_lane(scene.map_data)

        all_current_vertices_coord = scene.all_current_vertices_coord
        for added_traj in scene.all_trajectories:
            all_current_vertices_coord = np.vstack([all_current_vertices_coord, added_traj[0:1,0:2]])

        one_added_car = scene.added_cars_dict[added_car_name]
        if one_added_car['need_placement_and_motion'] is True: 
            
            scene.added_cars_dict[added_car_name]['need_placement_and_motion'] = False
            one_added_car = scene.added_cars_dict[added_car_name]

            # Scene-independent placement
            if one_added_car.get('x') is None:  # 'x' in one_added_car
                placement_result = vehicle_placement(
                    transformed_map_data,
                    all_current_vertices_coord,
                    one_added_car["direction"] if one_added_car["direction"] != 'random' else random.choice(['away','close']),
                    one_added_car["mode"],
                    one_added_car["distance_constraint"],
                    one_added_car["distance_min_max"],
                    "default"
                )
            # Scene-dependent placement
            else:
                placement_result = vehicle_placement_specific(
                    transformed_map_data,
                    all_current_vertices_coord,
                    np.array([one_added_car["x"],one_added_car["y"]]))

            if placement_result[0] is None: # can not placement
                del(scene.added_cars_dict[added_car_name])

            one_added_car['placement_result'] = placement_result #（xc,yc,theta,xs,ys,xe,ye)

            motion_result = vehicle_motion(
                transformed_map_data,
                scene.all_current_vertices[:,::2,:2] if scene.all_current_vertices.shape[0]!=0 else scene.all_current_vertices,
                placement_result=one_added_car['placement_result'],
                current_trajectory=scene.all_trajectories,
                v_init=0, 
                high_level_action_direction=one_added_car["action"],
                high_level_action_speed=one_added_car["speed"],
                total_len=scene.frames,
                idx=int(added_car_id)+1
            )

            
            if motion_result[0] is None: # can not generate motion
                del(scene.added_cars_dict[added_car_name])
                
            
            one_added_car['motion'] = motion_result
            scene.all_trajectories.append(motion_result)

            scene.added_cars_dict[added_car_name] = one_added_car
