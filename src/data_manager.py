import json

class DataManager():
    def __init__(self):
        pass

    def load(self, file_name):
        pass

    def save(self, file_name, grid, objects):
        grid_height = len(grid)
        grid_width = len(grid[0])

        out = {
            'grid_width': grid_width,
            'grid_height': grid_height,
            'objects': None}

        objects_dict = {}
        for object_id, obj in objects.items():
            obj_dict = {}

            objects_dict[obj.name] = obj_dict
        out['objects'] = objects_dict

        json_data = json.dumps(out, indent=4)
        print(json_data)