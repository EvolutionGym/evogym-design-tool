try:
    import OpenGL
    try:
        import OpenGL.GL   # this fails in <=2020 versions of Python on OS X 11.x
    except ImportError:
        from ctypes import util
        orig_util_find_library = util.find_library
        def new_util_find_library( name ):
            res = orig_util_find_library( name )
            if res: return res
            return '/System/Library/Frameworks/'+name+'.framework/'+name
        util.find_library = new_util_find_library
except ImportError:
    pass

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import colors
import utils

from evogym import Timer

class Viewer:

    has_init_glfw = False
    window_count = 1

    def __init__(self, window_name=None):

        if (not Viewer.has_init_glfw):
            if not glfw.init():
                raise RuntimeError('Could not initialize glfw.')
            Viewer.has_init_glfw = True

        if window_name == None:
            window_name = f'window_{Viewer.window_count}'
            Viewer.window_count += 1
        self.window_name = window_name

        x, y, fx, fy = glfw.get_monitor_workarea(glfw.get_primary_monitor())
        
        self.res_width = 600
        self.res_height = 400
        
        glfw.window_hint(glfw.MAXIMIZED, True)
        self.window = glfw.create_window(self.res_width, self.res_height, window_name, None, None)

        mx, my = glfw.get_window_size(self.window)

        self.res_width = mx - mx//4
        self.res_height = my
        self.window_data = (mx, my, fy)

        glfw.set_window_pos(self.window, 0, fy-my)

        self.debug = False
        if self.debug:
            glfw.set_window_size(self.window, self.res_width, self.res_height-200)
        else:
            glfw.set_window_size(self.window, self.res_width, self.res_height)

        if not self.window:
            glfw.terminate()
            raise RuntimeError(f'Could not create glfw window: {self.window_name}.')

        self.box_thickness = 1.0
        self.border_thickness = 0.05

        self.zoom = 50.0

        self.cam_width = 10
        self.cam_height = 10
        self.cam_pos_x = (self.cam_width*self.box_thickness + (self.cam_width+1)*self.border_thickness)/2
        self.cam_pos_y = (self.cam_height*self.box_thickness + (self.cam_height+1)*self.border_thickness)/2

        glfw.set_scroll_callback(self.window, self.on_scroll)
        self.scroll = 0

        self.currently_hovered = None
        self.currently_selected = None
        self.mouse_press = False
        self.mouse_held = False
        self.right_mouse_press = False
        self.right_mouse_held = False

        self.grab_x, self.grab_y = None, None
        self.init_cam_pos_x, self.init_cam_pos_y = None, None

        self.grid_width, self.grid_height = None, None

        self.arrow_cursor = glfw.create_standard_cursor(glfw.ARROW_CURSOR)
        self.hand_cursor = glfw.create_standard_cursor(glfw.HAND_CURSOR)
        self.cursor_mode = utils.ARROW_CURSOR

        self.timer = Timer(30)

    def load(self, file_name):
        self.currently_hovered = None
        self.currently_selected = None
    
    def change_gs(self, new_width, new_height):
        self.currently_hovered = None
        self.currently_selected = None

        height_diff = new_height - self.grid_height
        self.cam_pos_y += height_diff*(self.border_thickness + self.box_thickness)
        

    def get_mouse_press(self,):
        return glfw.get_mouse_button(self.window, 0)

    def get_right_mouse_press(self,):
        return glfw.get_mouse_button(self.window, 1)

    def get_mouse_pos(self,):
        return glfw.get_cursor_pos(self.window)

    def get_key_presses(self,):
        keys = {
            'left': glfw.KEY_LEFT, 'up': glfw.KEY_UP, 'right': glfw.KEY_RIGHT, 'down': glfw.KEY_DOWN,
            'w': glfw.KEY_W, 'a': glfw.KEY_A, 's': glfw.KEY_S, 'd': glfw.KEY_D,
            'z': glfw.KEY_Z, 'x': glfw.KEY_X, 'c': glfw.KEY_C, 'v': glfw.KEY_V, 'b': glfw.KEY_B, 'n': glfw.KEY_N}
        out = {}
        for key, value in keys.items():
            out[key] = glfw.get_key(self.window, value)
        return out

    def update_camera_pos(self,):
        if self.right_mouse_held:
            if self.right_mouse_press:
                self.grab_x, self.grab_y = self.get_mouse_pos()
                self.init_cam_pos_x, self.init_cam_pos_y = self.cam_pos_x, self.cam_pos_y
            cx, cy = self.get_mouse_pos()
            dx, dy = self.grab_x - cx, self.grab_y - cy

            dx, dy = (dx+1)/self.zoom, (-dy+1)/self.zoom
            self.cam_pos_x, self.cam_pos_y = self.init_cam_pos_x + dx, self.init_cam_pos_y - dy
        else:
            keys = self.get_key_presses()
            if keys['left'] or keys['a']:
                self.cam_pos_x -= 2/self.zoom
            if keys['right'] or keys['d']:
                self.cam_pos_x += 2/self.zoom
            if keys['up'] or keys['w']:
                self.cam_pos_y -= 2/self.zoom
            if keys['down'] or keys['s']:
                self.cam_pos_y += 2/self.zoom

    def mouse_to_node(self, grid):
        mx, my = self.get_mouse_pos()
        mx, my = mx/self.res_width*2-1, -(my/self.res_height*2-1)

        grid_height = len(grid)
        grid_width = len(grid[0])

        for i in range(grid_height):
            for j in range(grid_width):
                y = i
                x = j

                lx = self.border_thickness + x*(self.border_thickness + self.box_thickness)
                ly = self.border_thickness + y*(self.border_thickness + self.box_thickness)

                
                hx = lx + self.box_thickness
                hy = ly + self.box_thickness

                lx, ly = self.to_camera(lx, ly)
                hx, hy = self.to_camera(hx, hy)

                if mx > lx and mx < hx:
                    if my < ly and my > hy:
                        return grid[i][j], grid[i][j].id

        return (None, None)

    def mouse_to_edge(self, grid):
        mx, my = self.get_mouse_pos()
        mx, my = mx/self.res_width*2-1, -(my/self.res_height*2-1)

        grid_height = len(grid)
        grid_width = len(grid[0])

        for i in range(grid_height):
            for j in range(grid_width):
                y = i
                x = j

                if grid[i][j].type == utils.CELL_EMPTY:
                    continue

                for direction in ['l', 'r', 'u', 'd']:
                    
                    if direction == 'l':
                        other = utils.get_left(grid, grid[i][j].id)
                        if other == None or other.type == utils.CELL_EMPTY:
                            continue
                        lx, ly = (x*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.border_thickness, ly+self.box_thickness+self.border_thickness*2)

                    if direction == 'r':
                        other = utils.get_right(grid, grid[i][j].id)
                        if other == None or other.type == utils.CELL_EMPTY:
                            continue
                        lx, ly = ((x+1)*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.border_thickness, ly+self.box_thickness+self.border_thickness*2)

                    if direction == 'u':
                        other = utils.get_up(grid, grid[i][j].id)
                        if other == None or other.type == utils.CELL_EMPTY:
                            continue
                        lx, ly = (x*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.box_thickness+self.border_thickness*2, ly+self.border_thickness)

                    if direction == 'd':
                        other = utils.get_down(grid, grid[i][j].id)
                        if other == None or other.type == utils.CELL_EMPTY:
                            continue
                        lx, ly = (x*(self.border_thickness + self.box_thickness), (y+1)*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.box_thickness+self.border_thickness*2, ly+self.border_thickness)

                    lx, ly, hx, hy = utils.make_thicker(lx, ly, hx, hy, 5)
                    lx, ly = self.to_camera(lx, ly)
                    hx, hy = self.to_camera(hx, hy)

                    if mx > lx and mx < hx:
                        if my < ly and my > hy:
                            return utils.pair_to_string(grid[i][j].id, other.id)
            
        return None

    def on_scroll(self, a, b, c):
        self.scroll += c * 0.75

    def get_window_close(self,):
        return glfw.window_should_close(self.window)

    def update_resolution(self,):
        self.res_width, self.res_height = glfw.get_window_size(self.window)

    def update_zoom(self, ):
        if self.scroll != 0:
            self.zoom += self.scroll/abs(self.scroll)
        self.scroll = 0.25
        if abs(self.scroll) < 0.3:
            self.scroll = 0
        if self.zoom < 5:
            self.zoom = 5

        self.border_thickness = 0.02 + 2/self.zoom

    def update_hover(self, grid):
        self.currently_hovered = None

        node, node_id = self.mouse_to_node(grid)
        if node != None:
            self.currently_hovered = ('node', node, node_id, node.type)

        pair = self.mouse_to_edge(grid)
        if pair != None:
            self.currently_hovered = ('edge', pair)

        #print(self.currently_hovered)

    def update_selected(self, grid, node_to_object, just_altered):
        if self.mouse_press:
            if self.currently_selected != self.currently_hovered:
                
                hovered_object = None
                hovered = self.currently_hovered
                if hovered != None and hovered[0] == 'node' and utils.get_node_by_index(grid, hovered[2]).type != utils.CELL_EMPTY:
                    hovered_object = node_to_object[hovered[2]]
                if hovered != None and hovered[0] == 'edge':
                    a, b = tuple(hovered[1].split())
                    a, b = int(a), int(b)
                    hovered_object = node_to_object[a]

                selected_object = None
                selected = self.currently_selected
                if selected != None and selected[0] == 'node' and utils.get_node_by_index(grid, selected[2]).type != utils.CELL_EMPTY:
                    selected_object = node_to_object[selected[2]]
                if selected != None and selected[0] == 'edge':
                    a, b = tuple(selected[1].split())
                    a, b = int(a), int(b)
                    selected = node_to_object[a]

                if hovered_object != None and selected_object != hovered_object:
                    self.currently_selected = self.currently_hovered
                else:
                    self.currently_selected = None
            else:
                self.currently_selected = None
            
        if just_altered != None:
            self.currently_selected = just_altered

    def update_mouse_press(self,):

        if self.get_mouse_press():
            if self.mouse_held == True:
                self.mouse_press = False
            else:
                self.mouse_press = True
                self.mouse_held = True
        else:
            self.mouse_held = False
            self.mouse_press = False
    
    def update_right_mouse_press(self,):

        if self.get_right_mouse_press():
            if self.right_mouse_held == True:
                self.right_mouse_press = False
            else:
                self.right_mouse_press = True
                self.right_mouse_held = True
            self.cursor_mode = utils.HAND_CURSOR
        else:
            self.right_mouse_held = False
            self.right_mouse_press = False

    def update_cursor(self,):
        if self.cursor_mode == utils.ARROW_CURSOR:
            glfw.set_cursor(self.window, self.arrow_cursor)
        if self.cursor_mode == utils.HAND_CURSOR:
            glfw.set_cursor(self.window, self.hand_cursor)

    def render(self, grid, objects, hovered_object_id, selected_object_id, mode):
        
        glfw.make_context_current(self.window)
        glViewport(0, 0, self.res_width, self.res_height)
        self.reset()

        self.render_grid(grid, mode==utils.VOXELS)
        self.render_voxels(grid, mode==utils.VOXELS)
        self.render_edges(grid, objects, hovered_object_id, selected_object_id)
        if mode == utils.EDGES:
            self.render_selected_edges(grid)

        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def update_and_render(self, grid, objects, node_to_object, hovered_object_id, selected_object_id, just_altered, mode):

        self.cursor_mode = utils.ARROW_CURSOR
        self.grid_width, self.grid_height = len(grid[0]), len(grid)
        self.update_resolution()
        self.update_zoom()
        self.update_right_mouse_press()
        self.update_camera_pos()
        self.update_hover(grid)
        self.update_mouse_press()
        self.update_selected(grid, node_to_object, just_altered)
        self.update_cursor()

        if self.timer.should_step():
            self.render(grid, objects, hovered_object_id, selected_object_id, mode)
            self.timer.step()

    def reset(self,):
        glClearColor(*colors.CLEAR_COLOR)
        glClear(GL_COLOR_BUFFER_BIT)

    def render_edges(self, grid, objects, hovered_object_id, selected_object_id):
        
        grid_height = len(grid)
        grid_width = len(grid[0])

        for i in range(grid_height):
            for j in range(grid_width):
                y = i 
                x = j

                if grid[i][j].type == utils.CELL_EMPTY:
                    continue

                hovered = hovered_object_id != None and grid[i][j].id in objects[hovered_object_id].nodes 
                hovered = hovered or (selected_object_id != None and grid[i][j].id in objects[selected_object_id].nodes)

                for direction in ['l', 'r', 'u', 'd']:

                    if direction == 'l':
                        other = utils.get_left(grid, grid[i][j].id)
                        if other != None and other.type != utils.CELL_EMPTY and grid[i][j].id in other.neighbors:
                            continue
                        lx, ly = (x*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.border_thickness, ly+self.box_thickness+self.border_thickness*2)

                    if direction == 'r':
                        other = utils.get_right(grid, grid[i][j].id)
                        if other != None and other.type != utils.CELL_EMPTY and grid[i][j].id in other.neighbors:
                            continue
                        lx, ly = ((x+1)*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.border_thickness, ly+self.box_thickness+self.border_thickness*2)

                    if direction == 'u':
                        other = utils.get_up(grid, grid[i][j].id)
                        if other != None and other.type != utils.CELL_EMPTY and grid[i][j].id in other.neighbors:
                            continue
                        lx, ly = (x*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.box_thickness+self.border_thickness*2, ly+self.border_thickness)

                    if direction == 'd':
                        other = utils.get_down(grid, grid[i][j].id)
                        if other != None and other.type != utils.CELL_EMPTY and grid[i][j].id in other.neighbors:
                            continue
                        lx, ly = (x*(self.border_thickness + self.box_thickness), (y+1)*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.box_thickness+self.border_thickness*2, ly+self.border_thickness)


                    dim_factor = 1.15
                    dim_additive = 0.07
                    voxel_color = colors.EDGE_FULL
                    if hovered:
                        voxel_color = colors.EDGE_SELECTED
                        voxel_color = (voxel_color[0]*dim_factor+dim_additive, voxel_color[1]*dim_factor+dim_additive, voxel_color[2]*dim_factor+dim_additive)

                    glColor3f(*voxel_color)
                    
                    self.render_voxel(*self.to_camera(lx, ly), *self.to_camera(hx, hy))

        repeat_nodes = []
        if hovered_object_id != None:
            for node in objects[hovered_object_id].nodes:
                repeat_nodes.append(node)
        if selected_object_id != None:
            for node in objects[selected_object_id].nodes:
                repeat_nodes.append(node)

        for index in repeat_nodes:
            x, y = index%grid_width, index//grid_width
            i, j = y, x 

            if grid[i][j].type == utils.CELL_EMPTY:
                    continue

            hovered = hovered_object_id != None and grid[i][j].id in objects[hovered_object_id].nodes 
            hovered = hovered or (selected_object_id != None and grid[i][j].id in objects[selected_object_id].nodes)

            for direction in ['l', 'r', 'u', 'd']:

                if direction == 'l':
                    other = utils.get_left(grid, grid[i][j].id)
                    if other != None and other.type != utils.CELL_EMPTY and grid[i][j].id in other.neighbors:
                        continue
                    lx, ly = (x*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                    hx, hy = (lx+self.border_thickness, ly+self.box_thickness+self.border_thickness*2)

                if direction == 'r':
                    other = utils.get_right(grid, grid[i][j].id)
                    if other != None and other.type != utils.CELL_EMPTY and grid[i][j].id in other.neighbors:
                        continue
                    lx, ly = ((x+1)*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                    hx, hy = (lx+self.border_thickness, ly+self.box_thickness+self.border_thickness*2)

                if direction == 'u':
                    other = utils.get_up(grid, grid[i][j].id)
                    if other != None and other.type != utils.CELL_EMPTY and grid[i][j].id in other.neighbors:
                        continue
                    lx, ly = (x*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                    hx, hy = (lx+self.box_thickness+self.border_thickness*2, ly+self.border_thickness)

                if direction == 'd':
                    other = utils.get_down(grid, grid[i][j].id)
                    if other != None and other.type != utils.CELL_EMPTY and grid[i][j].id in other.neighbors:
                        continue
                    lx, ly = (x*(self.border_thickness + self.box_thickness), (y+1)*(self.border_thickness + self.box_thickness))
                    hx, hy = (lx+self.box_thickness+self.border_thickness*2, ly+self.border_thickness)


                dim_factor = 1.15
                dim_additive = 0.07
                voxel_color = colors.EDGE_FULL
                if hovered:
                    voxel_color = colors.EDGE_SELECTED
                    voxel_color = (voxel_color[0]*dim_factor+dim_additive, voxel_color[1]*dim_factor+dim_additive, voxel_color[2]*dim_factor+dim_additive)

                glColor3f(*voxel_color)
                
                self.render_voxel(*self.to_camera(lx, ly), *self.to_camera(hx, hy))

    def render_selected_edges(self, grid):
        
        grid_height = len(grid)
        grid_width = len(grid[0])

        for i in range(grid_height):
            for j in range(grid_width):
                y = i 
                x = j

                if grid[i][j].type == utils.CELL_EMPTY:
                    continue

                for direction in ['l', 'r', 'u', 'd']:
                    
                    if direction == 'l':
                        other = utils.get_left(grid, grid[i][j].id)
                        if other == None or other.type == utils.CELL_EMPTY:
                            continue
                        lx, ly = (x*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.border_thickness, ly+self.box_thickness+self.border_thickness*2)

                    if direction == 'r':
                        other = utils.get_right(grid, grid[i][j].id)
                        if other == None or other.type == utils.CELL_EMPTY:
                            continue
                        lx, ly = ((x+1)*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.border_thickness, ly+self.box_thickness+self.border_thickness*2)

                    if direction == 'u':
                        other = utils.get_up(grid, grid[i][j].id)
                        if other == None or other.type == utils.CELL_EMPTY:
                            continue
                        lx, ly = (x*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.box_thickness+self.border_thickness*2, ly+self.border_thickness)

                    if direction == 'd':
                        other = utils.get_down(grid, grid[i][j].id)
                        if other == None or other.type == utils.CELL_EMPTY:
                            continue
                        lx, ly = (x*(self.border_thickness + self.box_thickness), (y+1)*(self.border_thickness + self.box_thickness))
                        hx, hy = (lx+self.box_thickness+self.border_thickness*2, ly+self.border_thickness)

                    if not grid[i][j].id in other.neighbors:
                        edge_color = colors.EDGE_SELECTED
                    else:
                        edge_color = colors.EDGE_FULL

                    dim_factor = 1.07
                    dim_additive = 0.07
                    if self.currently_hovered != None and self.currently_hovered[0] == 'edge' and self.currently_hovered[1] == utils.pair_to_string(other.id, grid[i][j].id):
                        edge_color = (edge_color[0]*dim_factor+dim_additive, edge_color[1]*dim_factor+dim_additive, edge_color[2]*dim_factor+dim_additive)

                        glColor3f(*edge_color)

                        lx, ly, hx, hy = utils.make_thicker(lx, ly, hx, hy, 2)
                        self.render_voxel(*self.to_camera(lx, ly), *self.to_camera(hx, hy))

    def render_grid(self, grid, render_hover):
        grid_height = len(grid)
        grid_width = len(grid[0])

        pwidth = self.border_thickness + grid_width*(self.border_thickness + self.box_thickness)
        pheight = self.border_thickness + grid_height*(self.border_thickness + self.box_thickness)

        glColor3f(*colors.GRID_COLOR)
        glBegin(GL_QUADS)

        glVertex2f(*self.to_camera(0, 0))
        glVertex2f(*self.to_camera(pwidth, 0))
        glVertex2f(*self.to_camera(pwidth, pheight))
        glVertex2f(*self.to_camera(0, pheight))

        glEnd()

        for i in range(grid_height):
            for j in range(grid_width):
                y = i
                x = j

                if grid[i][j].type != utils.CELL_EMPTY:
                    continue
                
                voxel_color = colors.EMPTY_VOXEL
                
                dim_factor = 0.96
                dim_additive = -0.05
                if self.currently_hovered != None and self.currently_hovered[0] == 'node' and self.currently_hovered[2] == grid[i][j].id and render_hover:
                    voxel_color = (voxel_color[0]*dim_factor+dim_additive, voxel_color[1]*dim_factor+dim_additive, voxel_color[2]*dim_factor+dim_additive)

                glColor3f(*voxel_color)

                lx, ly = (x*(self.border_thickness + self.box_thickness)+self.border_thickness, y*(self.border_thickness + self.box_thickness)+self.border_thickness)
                hx, hy = (lx+self.box_thickness, ly+self.box_thickness)
                self.render_voxel(*self.to_camera(lx, ly), *self.to_camera(hx, hy))

    def render_voxels(self, grid, render_hover):
        grid_height = len(grid)
        grid_width = len(grid[0])

        for i in range(grid_height):
            for j in range(grid_width):
                y = i # grid_height - (i+1)
                x = j

                if grid[i][j].type == utils.CELL_EMPTY:
                    continue

                
                if grid[i][j].type == utils.CELL_RIGID:
                    voxel_color = colors.RIGID_VOXEL
                if grid[i][j].type == utils.CELL_SOFT:
                    voxel_color = colors.SOFT_VOXEL
                if grid[i][j].type == utils.CELL_ACT_H:
                    voxel_color = colors.ACT_H_VOXEL
                if grid[i][j].type == utils.CELL_ACT_V:
                    voxel_color = colors.ACT_V_VOXEL
                if grid[i][j].type == utils.CELL_FIXED:
                    voxel_color = colors.FIXED_VOXEL

                dim_factor = 1.05
                dim_additive = 0.07
                if self.currently_hovered != None and self.currently_hovered[0] == 'node' and self.currently_hovered[2] == grid[i][j].id and render_hover:
                    voxel_color = (voxel_color[0]*dim_factor+dim_additive, voxel_color[1]*dim_factor+dim_additive, voxel_color[2]*dim_factor+dim_additive)

                glColor3f(*voxel_color)
                
                lx, ly = (x*(self.border_thickness + self.box_thickness), y*(self.border_thickness + self.box_thickness))
                hx, hy = (lx+self.box_thickness+self.border_thickness, ly+self.box_thickness+self.border_thickness)
                self.render_voxel(*self.to_camera(lx, ly), *self.to_camera(hx, hy))

    def render_voxel(self, lx, ly, hx, hy):
        glBegin(GL_QUADS)
        glVertex2f(lx, ly)
        glVertex2f(lx, hy)
        glVertex2f(hx, hy)
        glVertex2f(hx, ly)
        glEnd()

    def to_camera(self, x, y):
        px, py = 2*(x-self.cam_pos_x)*self.zoom/self.res_width, -2*(y-self.cam_pos_y)*self.zoom/self.res_height
        return (px, py)

    def safe_close(self,):
        glfw.terminate()

