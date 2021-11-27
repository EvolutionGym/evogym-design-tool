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
                assert len(obj_data['indices'])  == len(obj_data['types'])
                assert len(obj_data['indices'])  == len(obj_data['neighbors'])

                objects[unnamed_obj_count-1] = utils.Object()
                curr_object = objects[unnamed_obj_count-1]
                curr_object.name = name

                # read in indices and types
                for i in range(len(obj_data['indices'])):
                    index_curr = utils.flip_y(obj_data['indices'][i], grid_width, grid_height)
                    type_curr = obj_data['types'][i]
                    curr_object.nodes[index_curr] = True
                    utils.get_node_by_index(grid, index_curr).type = type_curr

                    # set node neighbors
                    index_raw = obj_data['indices'][i]
                    for nei in obj_data['neighbors'][f'{index_raw}']:
                        utils.get_node_by_index(grid, index_curr).neighbors[utils.flip_y(nei, grid_width, grid_height)] = True

                # set node neighbors
                # for node in curr_object.nodes:
                #     neighbors = [
                #         utils.get_left(grid, node), 
                #         utils.get_right(grid, node), 
                #         utils.get_up(grid, node), 
                #         utils.get_down(grid, node)]
                #     for nei in neighbors:
                #         if nei != None and nei.id in curr_object.nodes:
                #             utils.get_node_by_index(grid, node).neighbors[nei.id] = True

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


        except Exception as e:
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
            indices = []
            types = []
            neighbors = {}
            for idx in obj.nodes:
                indices.append(utils.flip_y(idx, grid_width, grid_height))
                types.append(utils.get_node_by_index(grid, idx).type)

                ns = list(utils.get_node_by_index(grid, idx).neighbors.keys())
                for i in range(len(ns)):
                    ns[i] = utils.flip_y(ns[i], grid_width, grid_height)
                neighbors[utils.flip_y(idx, grid_width, grid_height)] = ns

            obj_dict = {'indices': indices, 'types': types, 'neighbors': neighbors}

            objects_dict[obj.name] = obj_dict
        out['objects'] = objects_dict

        
        with open(file_path, 'w') as outfile:
            json.dump(out, outfile, indent=4)