import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import colors
import utils

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

        self.res_width = 480
        self.res_height = 480
        self.window = glfw.create_window(self.res_width, self.res_height, window_name, None, None)

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

    def get_mouse_press(self,):
        return glfw.get_mouse_button(self.window, 0)

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

    def update_selected(self,):
        if self.mouse_press:
            self.currently_selected = self.currently_hovered

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

    def render(self, grid):
        self.update_resolution()
        self.update_zoom()
        self.update_camera_pos()
        self.update_hover(grid)
        self.update_mouse_press()
        self.update_selected()

        glfw.make_context_current(self.window)
        glViewport(0, 0, self.res_width, self.res_height)
        self.reset()

        self.render_grid(grid)
        self.render_voxels(grid)
        self.render_edges(grid)
        self.render_selected_edges(grid)

        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def reset(self,):
        glClearColor(*colors.CLEAR_COLOR)
        glClear(GL_COLOR_BUFFER_BIT)

    def render_edges(self, grid):
        
        grid_height = len(grid)
        grid_width = len(grid[0])

        for i in range(grid_height):
            for j in range(grid_width):
                y = i 
                x = j

                if grid[i][j].type == utils.CELL_EMPTY:
                    continue

                for direction in ['l', 'r', 'u', 'd']:
                    
                    voxel_color = colors.EDGE_FULL
                    hovered = False

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


                    dim_factor = 1.05
                    dim_additive = 0.07
                    #if self.currently_hovered != None and self.currently_hovered[0] == 'edge':
                    if hovered:
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
                        edge_color = colors.EDGE_EMPTY
                    else:
                        edge_color = colors.EDGE_FULL
                    dim_factor = 1.07
                    dim_additive = 0.07
                    if self.currently_hovered != None and self.currently_hovered[0] == 'edge' and self.currently_hovered[1] == utils.pair_to_string(other.id, grid[i][j].id):
                        edge_color = (edge_color[0]*dim_factor+dim_additive, edge_color[1]*dim_factor+dim_additive, edge_color[2]*dim_factor+dim_additive)

                        glColor3f(*edge_color)

                        lx, ly, hx, hy = utils.make_thicker(lx, ly, hx, hy, 2)
                        self.render_voxel(*self.to_camera(lx, ly), *self.to_camera(hx, hy))

    def render_grid(self, grid):
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
                if self.currently_hovered != None and self.currently_hovered[0] == 'node' and self.currently_hovered[2] == grid[i][j].id:
                    voxel_color = (voxel_color[0]*dim_factor+dim_additive, voxel_color[1]*dim_factor+dim_additive, voxel_color[2]*dim_factor+dim_additive)

                glColor3f(*voxel_color)

                lx, ly = (x*(self.border_thickness + self.box_thickness)+self.border_thickness, y*(self.border_thickness + self.box_thickness)+self.border_thickness)
                hx, hy = (lx+self.box_thickness, ly+self.box_thickness)
                self.render_voxel(*self.to_camera(lx, ly), *self.to_camera(hx, hy))

    def render_voxels(self, grid):
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
                if self.currently_hovered != None and self.currently_hovered[0] == 'node' and self.currently_hovered[2] == grid[i][j].id:
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

def main():
    v1 = Viewer()
    while True:
        v1.render()
        print(v1.get_mouse_pos())
    glfw.terminate()


if __name__ == "__main__":
    main()