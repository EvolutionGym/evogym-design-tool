import json
import utils
import os
import warnings

class DataManager():
    def __init__(self):
        pass

    def load(self, file_path):
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r') as infile:
                state = json.load(infile)

            grid_width = state['grid_width']
            grid_height = state['grid_height']

            grid = utils.make_blank_grid(grid_width, grid_height)
            utils.set_ids(grid)

            objects = {}
            node_to_object = {}
            unnamed_obj_count = 1

            # read in objects
            for name, obj_data in state['objects'].items():

                # assert lists of same length
                assert len(obj_data['indicies'])  == len(obj_data['types'])
                objects[unnamed_obj_count-1] = utils.Object()
                curr_object = objects[unnamed_obj_count-1]
                curr_object.name = name

                # read in indicies and types
                for i in range(len(obj_data['indicies'])):
                    index_curr = obj_data['indicies'][i]
                    type_curr = obj_data['types'][i]
                    curr_object.nodes[index_curr] = True
                    utils.get_node_by_index(grid, index_curr).type = type_curr

                # set node neighbors
                for node in curr_object.nodes:
                    neighbors = [
                        utils.get_left(grid, node), 
                        utils.get_right(grid, node), 
                        utils.get_up(grid, node), 
                        utils.get_down(grid, node)]
                    for nei in neighbors:
                        if nei != None and nei.id in curr_object.nodes:
                            utils.get_node_by_index(grid, node).neighbors[nei.id] = True

                #update object counts            
                unnamed_obj_count += 1  

            # set reverse dictionary
            node_to_object = {}
            for object_id, obj in objects.items():
                for node_id in obj.nodes:
                    node_to_object[node_id] = object_id

            # set unnamed object numbering
            for object_id, obj in objects.items():
                if 'new_object_' in obj.name:
                    remaining_name = obj.name[obj.name.index('new_object_')+len('new_object_'):]
                    try:
                        existing_int = int(remaining_name)
                        if unnamed_obj_count <= existing_int:
                            unnamed_obj_count = existing_int+1
                    except:
                        pass
        except:
            warnings.warn("Could not load file. Please check that your file has not been corrupted.")
            return None

        return grid_width, grid_height, grid, objects, node_to_object, unnamed_obj_count


    def save(self, file_path, grid, objects):
        grid_height = len(grid)
        grid_width = len(grid[0])

        out = {
            'grid_width': grid_width,
            'grid_height': grid_height,
            'objects': None}

        objects_dict = {}
        for object_id, obj in objects.items():
            indicies = []
            types = []
            for idx in obj.nodes:
                indicies.append(idx)
                types.append(utils.get_node_by_index(grid, idx).type)
            obj_dict = {'indicies': indicies, 'types': types}

            objects_dict[obj.name] = obj_dict
        out['objects'] = objects_dict

        
        with open(file_path, 'w') as outfile:
            json.dump(out, outfile, indent=4)