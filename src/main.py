import utils
import viewer
import env
import gui

import time
from tkinter import Tk

gui_master = Tk()
gui_master.title('EvoGym Design Interface GUI')

main_env = env.Env()
main_viewer = viewer.Viewer('EvoGym Design Interface')
gui_viewer = gui.GUI(gui_master, main_viewer.window_data)

gui_viewer.set_funcs(
    main_env.save, 
    main_env.load, 
    main_viewer.load, 
    main_env.change_gs,
    main_viewer.change_gs)

def main():
    while not main_viewer.get_window_close():

        main_viewer.update_and_render(
            main_env.grid, main_env.objects,
            main_env.node_to_object,
            main_env.hovered_object_id,
            main_env.selected_object_id,
            main_env.just_altered,
            main_env.mode)

        main_env.update(
            main_viewer.currently_hovered,
            main_viewer.currently_selected,
            main_viewer.mouse_press,
            main_viewer.mouse_held,
            main_viewer.get_key_presses(),
            gui_viewer.mode_data)

        gui_viewer.update(
            main_env.grid, 
            main_env.objects,
            main_env.need_to_update_objects,
            main_env.hovered_object_id, 
            main_env.selected_object_id,
            main_viewer.get_key_presses())

        #utils.get_objects(main_env.grid)
        #time.sleep(1)

        # print(main_viewer.get_key_presses())

    main_viewer.safe_close()
if __name__ == "__main__":
    main()
